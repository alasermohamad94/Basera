"""
خدمة التفريغ الصوتي باستخدام Whisper أو APIs أخرى
"""
import os
from django.conf import settings
from django.core.files.storage import default_storage
import tempfile

# استيراد whisper بشكل اختياري
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    whisper = None


class TranscriptionService:
    """خدمة التفريغ الصوتي"""
    
    _model = None
    
    @classmethod
    def get_model(cls):
        """تحميل نموذج Whisper (يتم تحميله مرة واحدة فقط)"""
        if not WHISPER_AVAILABLE:
            print("Whisper is not installed. Please install it with: pip install openai-whisper")
            return None
        
        if cls._model is None:
            try:
                # يمكن استخدام نموذج أصغر للسرعة: tiny, base, small, medium, large
                # tiny: الأسرع، base: متوازن (افتراضي)، large: الأكثر دقة
                model_name = getattr(settings, 'WHISPER_MODEL', 'base')
                cls._model = whisper.load_model(model_name)
            except Exception as e:
                print(f"Error loading Whisper model: {e}")
                print("Note: Make sure ffmpeg is installed")
                return None
        return cls._model
    
    @classmethod
    def transcribe_audio(cls, audio_file_path, language='ar'):
        """
        تفريغ الملف الصوتي إلى نص
        
        Args:
            audio_file_path: مسار الملف الصوتي
            language: اللغة (ar للعربية)
        
        Returns:
            str: النص المفروغ
        """
        try:
            model = cls.get_model()
            if model is None:
                return None
            
            # تفريغ الصوت
            result = model.transcribe(
                audio_file_path,
                language=language,
                task="transcribe"
            )
            
            return result.get("text", "")
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return None
    
    @classmethod
    def transcribe_uploaded_file(cls, uploaded_file):
        """
        تفريغ ملف مرفوع من Django
        
        Args:
            uploaded_file: Django UploadedFile
        
        Returns:
            str: النص المفروغ
        """
        try:
            # حفظ الملف مؤقتاً
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                for chunk in uploaded_file.chunks():
                    tmp_file.write(chunk)
                tmp_file_path = tmp_file.name
            
            # تفريغ الصوت
            text = cls.transcribe_audio(tmp_file_path)
            
            # حذف الملف المؤقت
            os.unlink(tmp_file_path)
            
            return text
        except Exception as e:
            print(f"Error processing uploaded file: {e}")
            return None

