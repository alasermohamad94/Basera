from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import TranscriptionReview, AudioRecording
from .serializers import TranscriptionReviewSerializer, AudioRecordingSerializer
from lessons.models import Lesson


class TranscriptionReviewViewSet(viewsets.ModelViewSet):
    queryset = TranscriptionReview.objects.all()
    serializer_class = TranscriptionReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'lesson']

    def get_queryset(self):
        # المتطوعون يرون فقط المراجعات الخاصة بهم
        if self.request.user.user_type == 'volunteer':
            return TranscriptionReview.objects.filter(reviewer=self.request.user)
        # المديرون يرون كل المراجعات
        return TranscriptionReview.objects.all()

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """اعتماد المراجعة وتحديث نص الدرس"""
        review = self.get_object()
        review.status = 'approved'
        review.save()
        
        # تحديث نص الدرس بالنص بعد المراجعة
        lesson = review.lesson
        lesson.transcribed_text = review.reviewed_text
        lesson.transcribed_text_reviewed = True
        lesson.reviewed_by = review.reviewer
        lesson.save()

        return Response({'message': 'تم اعتماد المراجعة وتحديث الدرس'})


class AudioRecordingViewSet(viewsets.ModelViewSet):
    queryset = AudioRecording.objects.all()
    serializer_class = AudioRecordingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    def get_queryset(self):
        # المستخدمون يرون فقط تسجيلاتهم
        if self.request.user.user_type != 'admin':
            return AudioRecording.objects.filter(recorded_by=self.request.user)
        return AudioRecording.objects.all()

    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)

    @action(detail=False, methods=['get'])
    def pending_transcription(self, request):
        """الحصول على التسجيلات التي تحتاج تفريغ"""
        recordings = AudioRecording.objects.filter(status='pending')
        serializer = self.get_serializer(recordings, many=True)
        return Response(serializer.data)

