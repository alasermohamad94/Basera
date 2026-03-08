from rest_framework import serializers
from .models import TranscriptionReview, AudioRecording
from lessons.serializers import LessonSerializer


class TranscriptionReviewSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    reviewer_username = serializers.CharField(source='reviewer.username', read_only=True)

    class Meta:
        model = TranscriptionReview
        fields = ['id', 'lesson', 'lesson_title', 'reviewer', 'reviewer_username',
                  'reviewed_text', 'comments', 'status', 'reviewed_at', 'updated_at']
        read_only_fields = ['reviewer']


class AudioRecordingSerializer(serializers.ModelSerializer):
    recorded_by_username = serializers.CharField(source='recorded_by.username', read_only=True)
    audio_file_url = serializers.SerializerMethodField()

    class Meta:
        model = AudioRecording
        fields = ['id', 'title', 'description', 'audio_file', 'audio_file_url',
                  'recorded_by', 'recorded_by_username', 'status', 'transcribed_text',
                  'notes', 'created_at', 'updated_at']
        read_only_fields = ['recorded_by', 'transcribed_text']

    def get_audio_file_url(self, obj):
        if obj.audio_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.audio_file.url)
        return None

