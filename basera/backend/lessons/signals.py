"""
إشارات Django لتحويل PDF/نص إلى صوت تلقائياً عند حفظ الدرس
"""
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.files.base import ContentFile
from django.conf import settings
from django.db import transaction
import os
import logging
from .models import Lesson
from .text_conversion_service import TextConversionService
from .tts_service import TTSService

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Lesson)
def extract_text_from_pdf(sender, instance, **kwargs):
    """
    إشارة لاستخراج النص من PDF أو text_content قبل حفظ الدرس
    """
    # إذا حُدّث محتوى النص يدوياً نزامن النص المفروغ حتى يظهر في التطبيق
    if instance.pk:
        try:
            old = Lesson.objects.get(pk=instance.pk)
            new_text = (instance.text_content or '').strip()
            old_text = (old.text_content or '').strip()
            if new_text and new_text != old_text:
                instance.transcribed_text = instance.text_content
        except Lesson.DoesNotExist:
            pass

    # استخراج النص من PDF أو text_content إذا كان هناك نص ولم يتم استخراجه بعد
    if (instance.pdf_file or instance.text_content) and not instance.transcribed_text:
        # تحديث حالة التحويل
        instance.conversion_status = 'extracting_text'
        instance.conversion_progress = 10
        instance.conversion_error = None
        
        extracted_text = TextConversionService.process_lesson_text(instance)
        if extracted_text:
            instance.transcribed_text = extracted_text
            instance.conversion_status = 'text_extracted'
            instance.conversion_progress = 50
            logger.info(f"تم استخراج النص من PDF/نص للدرس: {instance.title}")
        else:
            instance.conversion_status = 'failed'
            instance.conversion_progress = 0
            instance.conversion_error = 'فشل استخراج النص من PDF'


@receiver(post_save, sender=Lesson)
def convert_text_to_audio(sender, instance, created, **kwargs):
    """
    إشارة لتحويل النص إلى صوت بعد حفظ الدرس
    """
    # التحويل فقط إذا:
    # 1. يوجد نص مفروغ
    # 2. لا يوجد ملف صوتي بالفعل
    # 3. النص غير فارغ
    
    if not instance.transcribed_text or not instance.transcribed_text.strip():
        return
    
    # إذا كان هناك ملف صوتي موجود بالفعل، لا نحول مرة أخرى
    if instance.audio_file:
        audio_path = os.path.join(settings.MEDIA_ROOT, instance.audio_file.name)
        if os.path.exists(audio_path):
            logger.info(f"الملف الصوتي موجود بالفعل للدرس: {instance.title}")
            return
    
    # استخدام transaction.on_commit لتأجيل العملية حتى انتهاء المعاملة
    def convert_after_commit():
        try:
            lesson_id = instance.pk
            # حفظ البيانات المهمة قبل commit
            transcribed_text_content = instance.transcribed_text
            
            # التحقق من وجود النص
            if not transcribed_text_content or not transcribed_text_content.strip():
                Lesson.objects.filter(pk=lesson_id).update(
                    conversion_status='failed',
                    conversion_error='لا يوجد نص للتحويل'
                )
                return
            
            # استخدام filter().first() لتجنب recursion error
            lesson = Lesson.objects.filter(pk=lesson_id).first()
            if not lesson:
                logger.error(f"الدرس غير موجود: {lesson_id}")
                return
            
            # التحقق من وجود ملف صوتي
            if lesson.audio_file:
                audio_path = os.path.join(settings.MEDIA_ROOT, lesson.audio_file.name)
                if os.path.exists(audio_path):
                    Lesson.objects.filter(pk=lesson_id).update(
                        conversion_status='completed',
                        conversion_progress=100
                    )
                    return
            
            # تحديث حالة التحويل إلى "جاري تحويل النص إلى صوت"
            Lesson.objects.filter(pk=lesson_id).update(
                conversion_status='converting_audio',
                conversion_progress=60,
                conversion_error=None
            )
            
            # إنشاء اسم ملف صوتي
            audio_filename = f"lesson_{lesson_id}_{lesson.title[:50]}.mp3"
            audio_filename = audio_filename.replace(' ', '_').replace('/', '_').replace('\\', '_')
            
            # إنشاء مسار مؤقت للملف
            import tempfile
            temp_dir = tempfile.gettempdir()
            temp_audio_path = os.path.join(temp_dir, audio_filename)
            
            # تحديث التقدم
            Lesson.objects.filter(pk=lesson_id).update(conversion_progress=70)
            
            # تحويل النص إلى صوت
            try:
                result_path = TTSService.convert_text_to_speech(
                    transcribed_text_content,
                    output_path=temp_audio_path,
                    use_gtts=True,  # استخدام gTTS (أفضل للعربية)
                    fallback_to_pyttsx3=True  # استخدام pyttsx3 كبديل عند فشل gTTS
                )
            except Exception as tts_error:
                error_msg = f"خطأ في خدمة التحويل: {str(tts_error)}"
                logger.error(f"فشل تحويل النص إلى صوت للدرس ID {lesson_id}: {tts_error}", exc_info=True)
                Lesson.objects.filter(pk=lesson_id).update(
                    conversion_status='failed',
                    conversion_progress=0,
                    conversion_error=error_msg[:500]
                )
                return
            
            # تحديث التقدم
            Lesson.objects.filter(pk=lesson_id).update(conversion_progress=85)
            
            if result_path and os.path.exists(result_path):
                # إعادة تحميل الدرس لحفظ الملف
                lesson = Lesson.objects.filter(pk=lesson_id).first()
                if lesson:
                    # حفظ الملف الصوتي في الحقل
                    with open(result_path, 'rb') as audio_file:
                        lesson.audio_file.save(
                            audio_filename,
                            ContentFile(audio_file.read()),
                            save=True
                        )
                    
                    # حذف الملف المؤقت
                    if os.path.exists(result_path):
                        try:
                            os.remove(result_path)
                        except Exception as e:
                            logger.warning(f"فشل حذف الملف المؤقت: {e}")
                    
                    # تحديث مدة الصوت (تقريبي: 150 كلمة في الدقيقة)
                    word_count = len(transcribed_text_content.split())
                    estimated_duration = int((word_count / 150) * 60)  # بالثواني
                    
                    # تحديث الحالة إلى "اكتمل" باستخدام update لتجنب signals
                    Lesson.objects.filter(pk=lesson_id).update(
                        conversion_status='completed',
                        conversion_progress=100,
                        duration=estimated_duration,
                        conversion_error=None
                    )
                    
                    logger.info(f"تم تحويل النص إلى صوت للدرس: {lesson.title}")
            else:
                error_detail = 'لم يتم إنشاء ملف صوتي'
                if result_path:
                    error_detail = f'الملف غير موجود: {result_path}'
                Lesson.objects.filter(pk=lesson_id).update(
                    conversion_status='failed',
                    conversion_progress=0,
                    conversion_error=f'فشل تحويل النص إلى صوت: {error_detail}'
                )
                logger.warning(f"فشل تحويل النص إلى صوت للدرس ID: {lesson_id} - {error_detail}")
        
        except Exception as e:
            error_msg = str(e)[:500]  # تحديد طول رسالة الخطأ
            logger.error(f"خطأ في تحويل النص إلى صوت للدرس ID {instance.pk}: {e}", exc_info=True)
            try:
                Lesson.objects.filter(pk=instance.pk).update(
                    conversion_status='failed',
                    conversion_progress=0,
                    conversion_error=error_msg
                )
            except Exception as update_error:
                logger.error(f"فشل تحديث حالة الخطأ: {update_error}")
    
    # تأجيل العملية حتى انتهاء المعاملة
    transaction.on_commit(convert_after_commit)
