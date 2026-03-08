"""
Views للتفريغ الصوتي
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.files.uploadedfile import InMemoryUploadedFile
from .transcription_service import TranscriptionService, WHISPER_AVAILABLE
from .models import Lesson


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transcribe_audio(request):
    """
    تفريغ ملف صوتي مرفوع
    
    POST /api/lessons/transcribe/
    Body: multipart/form-data
    - audio_file: الملف الصوتي
    - lesson_id (optional): ID الدرس إذا كان موجوداً
    """
    try:
        if not WHISPER_AVAILABLE:
            return Response(
                {'error': 'Whisper غير مثبت. يرجى تثبيته باستخدام: pip install openai-whisper'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        if 'audio_file' not in request.FILES:
            return Response(
                {'error': 'لم يتم رفع ملف صوتي'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        audio_file = request.FILES['audio_file']
        lesson_id = request.data.get('lesson_id')
        
        # تفريغ الصوت
        transcribed_text = TranscriptionService.transcribe_uploaded_file(audio_file)
        
        if transcribed_text is None:
            return Response(
                {'error': 'فشل تفريغ الملف الصوتي. تأكد من تثبيت ffmpeg'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # إذا كان هناك lesson_id، تحديث الدرس
        if lesson_id:
            try:
                lesson = Lesson.objects.get(id=lesson_id)
                lesson.transcribed_text = transcribed_text
                lesson.save()
            except Lesson.DoesNotExist:
                pass
        
        return Response({
            'transcribed_text': transcribed_text,
            'message': 'تم التفريغ بنجاح'
        })
    
    except Exception as e:
        return Response(
            {'error': f'خطأ في المعالجة: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transcribe_lesson_audio(request, lesson_id):
    """
    تفريغ ملف صوتي لدرس معين
    
    POST /api/lessons/{lesson_id}/transcribe/
    """
    try:
        if not WHISPER_AVAILABLE:
            return Response(
                {'error': 'Whisper غير مثبت. يرجى تثبيته باستخدام: pip install openai-whisper'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        lesson = Lesson.objects.get(id=lesson_id)
        
        if not lesson.audio_file:
            return Response(
                {'error': 'الدرس لا يحتوي على ملف صوتي'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # تفريغ الصوت
        transcribed_text = TranscriptionService.transcribe_audio(lesson.audio_file.path)
        
        if transcribed_text is None:
            return Response(
                {'error': 'فشل تفريغ الملف الصوتي. تأكد من تثبيت ffmpeg'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # تحديث الدرس
        lesson.transcribed_text = transcribed_text
        lesson.save()
        
        return Response({
            'transcribed_text': transcribed_text,
            'message': 'تم التفريغ بنجاح'
        })
    
    except Lesson.DoesNotExist:
        return Response(
            {'error': 'الدرس غير موجود'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'خطأ في المعالجة: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

