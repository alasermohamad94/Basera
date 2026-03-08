from django.db import models
from django.contrib.auth import get_user_model
from lessons.models import Lesson

User = get_user_model()


class TranscriptionReview(models.Model):
    """مراجعة التفريغ الصوتي"""
    STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('approved', 'معتمد'),
        ('needs_revision', 'يحتاج مراجعة'),
    ]

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='transcription_reviews', verbose_name='الدرس')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transcription_reviews', verbose_name='المراجع')
    reviewed_text = models.TextField(verbose_name='النص بعد المراجعة')
    comments = models.TextField(blank=True, null=True, verbose_name='تعليقات')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='الحالة')
    reviewed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'مراجعة تفريغ'
        verbose_name_plural = 'مراجعات التفريغ'
        ordering = ['-reviewed_at']

    def __str__(self):
        return f"{self.lesson.title} - {self.reviewer.username}"


class AudioRecording(models.Model):
    """تسجيل صوتي جديد من المتطوع"""
    STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('transcribed', 'تم التفريغ'),
        ('reviewed', 'تمت المراجعة'),
        ('published', 'منشور'),
    ]

    title = models.CharField(max_length=300, verbose_name='العنوان')
    description = models.TextField(blank=True, null=True, verbose_name='الوصف')
    audio_file = models.FileField(upload_to='volunteers/audio/', verbose_name='الملف الصوتي')
    recorded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recordings', verbose_name='المسجل')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='الحالة')
    transcribed_text = models.TextField(blank=True, null=True, verbose_name='النص المفروغ')
    notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'تسجيل صوتي'
        verbose_name_plural = 'التسجيلات الصوتية'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

