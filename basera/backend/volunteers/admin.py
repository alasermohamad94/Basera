from django.contrib import admin
from .models import TranscriptionReview, AudioRecording


@admin.register(TranscriptionReview)
class TranscriptionReviewAdmin(admin.ModelAdmin):
    list_display = ['lesson', 'reviewer', 'status', 'reviewed_at']
    list_filter = ['status', 'reviewed_at']
    search_fields = ['lesson__title', 'reviewer__username']


@admin.register(AudioRecording)
class AudioRecordingAdmin(admin.ModelAdmin):
    list_display = ['title', 'recorded_by', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'description']

