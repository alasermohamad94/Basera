from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TranscriptionReviewViewSet, AudioRecordingViewSet

router = DefaultRouter()
router.register(r'transcriptions', TranscriptionReviewViewSet, basename='transcription-review')
router.register(r'recordings', AudioRecordingViewSet, basename='audio-recording')

urlpatterns = [
    path('', include(router.urls)),
]

