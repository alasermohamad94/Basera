"""
خدمة تحويل النص إلى صوت (Text-to-Speech)
"""
import os
import logging
import tempfile
import time
from pathlib import Path
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)

try:
    from gtts import gTTS
    from gtts.tts import gTTSError
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    gTTSError = Exception
    logger.warning("gTTS غير مثبت. لن يعمل تحويل النص إلى صوت.")

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    logger.warning("pyttsx3 غير مثبت. لن يعمل تحويل النص إلى صوت المحلي.")


class TTSService:
    """خدمة تحويل النص إلى صوت"""

    # إعدادات إعادة المحاولة
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # ثواني

    @staticmethod
    def _retry_gtts_chunk(chunk, lang, temp_path, max_retries=3):
        """
        محاولة تحويل جزء من النص مع إعادة المحاولة
        
        Args:
            chunk: جزء النص المراد تحويله
            lang: اللغة
            temp_path: مسار الملف المؤقت
            max_retries: عدد محاولات إعادة المحاولة
            
        Returns:
            bool: True إذا نجح التحويل، False إذا فشل
        """
        for attempt in range(1, max_retries + 1):
            try:
                tts = gTTS(text=chunk, lang=lang, slow=False)
                tts.save(temp_path)
                if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                    logger.info(f"تم تحويل الجزء إلى صوت (المحاولة {attempt})")
                    return True
                else:
                    logger.warning(f"الملف الصوتي فارغ (المحاولة {attempt})")
            except gTTSError as e:
                error_msg = str(e).lower()
                # بعض الأخطاء لا يجب إعادة المحاولة لها
                if 'connection' in error_msg or 'network' in error_msg or 'timeout' in error_msg:
                    if attempt < max_retries:
                        wait_time = TTSService.RETRY_DELAY * attempt
                        logger.warning(f"خطأ في الاتصال (المحاولة {attempt}/{max_retries}). انتظار {wait_time} ثانية...")
                        time.sleep(wait_time)
                        continue
                logger.error(f"خطأ في gTTS (المحاولة {attempt}): {e}")
            except Exception as e:
                error_msg = str(e).lower()
                if attempt < max_retries and ('connection' in error_msg or 'network' in error_msg or 'timeout' in error_msg):
                    wait_time = TTSService.RETRY_DELAY * attempt
                    logger.warning(f"خطأ عام (المحاولة {attempt}/{max_retries}). انتظار {wait_time} ثانية...")
                    time.sleep(wait_time)
                    continue
                logger.error(f"خطأ غير متوقع (المحاولة {attempt}): {e}", exc_info=True)
        
        return False

    @staticmethod
    def text_to_speech_gtts(text, lang='ar', output_path=None, max_retries=None):
        """
        تحويل النص إلى صوت باستخدام gTTS (Google Text-to-Speech)
        
        Args:
            text: النص المراد تحويله
            lang: اللغة (افتراضي: 'ar' للعربية)
            output_path: مسار الملف الصوتي الناتج
            max_retries: عدد محاولات إعادة المحاولة (افتراضي: MAX_RETRIES)
            
        Returns:
            str: مسار الملف الصوتي أو None
        """
        if not GTTS_AVAILABLE:
            logger.error("gTTS غير مثبت. لا يمكن تحويل النص إلى صوت.")
            return None
            
        if not text or not text.strip():
            logger.warning("النص فارغ. لا يمكن تحويله إلى صوت.")
            return None

        if max_retries is None:
            max_retries = TTSService.MAX_RETRIES

        try:
            # تقسيم النص إلى أجزاء (gTTS له حد أقصى ~5000 حرف)
            max_chunk_length = 4500
            text_chunks = []
            
            # تقسيم النص إلى أجزاء
            words = text.split()
            current_chunk = []
            current_length = 0
            
            for word in words:
                word_length = len(word) + 1  # +1 للفراغ
                if current_length + word_length > max_chunk_length and current_chunk:
                    text_chunks.append(' '.join(current_chunk))
                    current_chunk = [word]
                    current_length = word_length
                else:
                    current_chunk.append(word)
                    current_length += word_length
            
            if current_chunk:
                text_chunks.append(' '.join(current_chunk))

            logger.info(f"تم تقسيم النص إلى {len(text_chunks)} جزء")

            # إنشاء ملف صوتي لكل جزء ودمجها
            audio_files = []
            temp_dir = tempfile.gettempdir()
            failed_chunks = 0
            
            for i, chunk in enumerate(text_chunks):
                temp_path = os.path.join(temp_dir, f"temp_audio_{i}_{os.getpid()}.mp3")
                
                # محاولة تحويل الجزء مع إعادة المحاولة
                if TTSService._retry_gtts_chunk(chunk, lang, temp_path, max_retries):
                    audio_files.append(temp_path)
                    logger.info(f"تم تحويل الجزء {i+1}/{len(text_chunks)} إلى صوت")
                else:
                    logger.error(f"فشل تحويل الجزء {i+1}/{len(text_chunks)} بعد {max_retries} محاولات")
                    failed_chunks += 1
                    # حذف الملف المؤقت إذا كان موجوداً
                    if os.path.exists(temp_path):
                        try:
                            os.remove(temp_path)
                        except:
                            pass

            # إذا فشل تحويل جميع الأجزاء
            if len(audio_files) == 0:
                logger.error(f"فشل تحويل جميع الأجزاء ({failed_chunks}/{len(text_chunks)})")
                return None

            # إذا نجح تحويل بعض الأجزاء فقط
            if failed_chunks > 0:
                logger.warning(f"نجح تحويل {len(audio_files)}/{len(text_chunks)} جزء فقط")

            # دمج الملفات الصوتية إذا كان هناك أكثر من جزء
            if len(audio_files) > 1:
                try:
                    from pydub import AudioSegment
                    
                    combined = AudioSegment.empty()
                    for audio_file in audio_files:
                        if os.path.exists(audio_file):
                            try:
                                audio = AudioSegment.from_mp3(audio_file)
                                combined += audio
                            except Exception as e:
                                logger.error(f"فشل قراءة الملف الصوتي {audio_file}: {e}")
                                continue
                            finally:
                                # حذف الملف المؤقت
                                try:
                                    os.remove(audio_file)
                                except Exception as e:
                                    logger.warning(f"فشل حذف الملف المؤقت {audio_file}: {e}")
                    
                    # حفظ الملف المدمج
                    if output_path:
                        combined.export(output_path, format="mp3")
                        logger.info(f"تم دمج {len(audio_files)} جزء وإنشاء ملف صوتي: {output_path}")
                        return output_path
                except Exception as e:
                    logger.error(f"فشل دمج الملفات الصوتية: {e}", exc_info=True)
                    # استخدام الملف الأول فقط
                    if audio_files:
                        if output_path:
                            import shutil
                            try:
                                shutil.move(audio_files[0], output_path)
                                # حذف الملفات المؤقتة الأخرى
                                for temp_file in audio_files[1:]:
                                    if os.path.exists(temp_file):
                                        try:
                                            os.remove(temp_file)
                                        except:
                                            pass
                                logger.info(f"تم حفظ الملف الأول فقط: {output_path}")
                                return output_path
                            except Exception as move_error:
                                logger.error(f"فشل نقل الملف: {move_error}")
            elif len(audio_files) == 1:
                # ملف واحد فقط
                if output_path:
                    import shutil
                    try:
                        shutil.move(audio_files[0], output_path)
                        logger.info(f"تم إنشاء ملف صوتي: {output_path}")
                        return output_path
                    except Exception as e:
                        logger.error(f"فشل نقل الملف: {e}", exc_info=True)

            return None

        except Exception as e:
            logger.error(f"فشل تحويل النص إلى صوت باستخدام gTTS: {e}", exc_info=True)
            return None

    @staticmethod
    def text_to_speech_pyttsx3(text, output_path=None, rate=150):
        """
        تحويل النص إلى صوت باستخدام pyttsx3 (محلي - لا يحتاج إنترنت)
        
        Args:
            text: النص المراد تحويله
            output_path: مسار الملف الصوتي الناتج
            rate: سرعة الكلام (افتراضي: 150)
            
        Returns:
            str: مسار الملف الصوتي أو None
        """
        if not PYTTSX3_AVAILABLE:
            logger.error("pyttsx3 غير مثبت. لا يمكن تحويل النص إلى صوت.")
            return None
            
        if not text or not text.strip():
            logger.warning("النص فارغ. لا يمكن تحويله إلى صوت.")
            return None

        try:
            engine = pyttsx3.init()
            
            # إعدادات الصوت
            engine.setProperty('rate', rate)
            engine.setProperty('volume', 1.0)
            
            # البحث عن صوت عربي (إن وجد)
            try:
                voices = engine.getProperty('voices')
                arabic_voice = None
                for voice in voices:
                    voice_name = voice.name.lower() if hasattr(voice, 'name') else ''
                    voice_id = voice.id.lower() if hasattr(voice, 'id') else ''
                    if 'arabic' in voice_name or 'ar' in voice_id:
                        arabic_voice = voice.id
                        logger.info(f"تم العثور على صوت عربي: {voice_name}")
                        break
                
                if arabic_voice:
                    engine.setProperty('voice', arabic_voice)
            except Exception as voice_error:
                logger.warning(f"فشل البحث عن صوت عربي: {voice_error}")
            
            # حفظ الصوت في ملف
            if output_path:
                # التأكد من وجود المجلد
                os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
                
                engine.save_to_file(text, output_path)
                engine.runAndWait()
                
                # التحقق من وجود الملف
                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    logger.info(f"تم إنشاء ملف صوتي باستخدام pyttsx3: {output_path}")
                    return output_path
                else:
                    logger.error("فشل pyttsx3 في إنشاء ملف صوتي (الملف غير موجود أو فارغ)")
                    return None
            else:
                logger.warning("لم يتم تحديد مسار الإخراج.")
                return None

        except Exception as e:
            logger.error(f"فشل تحويل النص إلى صوت باستخدام pyttsx3: {e}", exc_info=True)
            return None
        finally:
            # تنظيف المحرك
            try:
                engine.stop()
            except:
                pass

    @staticmethod
    def convert_text_to_speech(text, output_path=None, use_gtts=True, fallback_to_pyttsx3=True):
        """
        تحويل النص إلى صوت مع إمكانية استخدام البديل التلقائي
        
        Args:
            text: النص المراد تحويله
            output_path: مسار الملف الصوتي الناتج
            use_gtts: استخدام gTTS أولاً (True) أو pyttsx3 (False)
            fallback_to_pyttsx3: استخدام pyttsx3 كبديل عند فشل gTTS
            
        Returns:
            str: مسار الملف الصوتي أو None
        """
        if not text or not text.strip():
            logger.warning("النص فارغ. لا يمكن تحويله إلى صوت.")
            return None

        # محاولة استخدام gTTS أولاً إذا كان مفعلاً ومتاحاً
        if use_gtts and GTTS_AVAILABLE:
            logger.info("محاولة تحويل النص إلى صوت باستخدام gTTS...")
            result = TTSService.text_to_speech_gtts(text, lang='ar', output_path=output_path)
            
            if result and os.path.exists(result):
                logger.info("تم تحويل النص إلى صوت بنجاح باستخدام gTTS")
                return result
            else:
                logger.warning("فشل تحويل النص إلى صوت باستخدام gTTS")
                # استخدام pyttsx3 كبديل إذا كان مفعلاً
                if fallback_to_pyttsx3 and PYTTSX3_AVAILABLE:
                    logger.info("محاولة استخدام pyttsx3 كبديل...")
                    result = TTSService.text_to_speech_pyttsx3(text, output_path=output_path)
                    if result and os.path.exists(result):
                        logger.info("تم تحويل النص إلى صوت بنجاح باستخدام pyttsx3 كبديل")
                        return result
                    else:
                        logger.error("فشل تحويل النص إلى صوت باستخدام pyttsx3 أيضاً")
        
        # استخدام pyttsx3 مباشرة إذا كان gTTS غير متاح أو غير مفعّل
        elif PYTTSX3_AVAILABLE:
            logger.info("استخدام pyttsx3 مباشرة...")
            result = TTSService.text_to_speech_pyttsx3(text, output_path=output_path)
            if result and os.path.exists(result):
                return result
        
        # لا توجد مكتبة متاحة
        logger.error("لا توجد مكتبة TTS متاحة. يرجى تثبيت gTTS أو pyttsx3.")
        return None