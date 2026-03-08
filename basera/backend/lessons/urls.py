from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    GradeViewSet, CategoryViewSet, LessonViewSet,
    VolunteerRoleViewSet
)
from .transcription_views import transcribe_audio, transcribe_lesson_audio

router = DefaultRouter()
router.register(r'grades', GradeViewSet, basename='grade')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'lessons', LessonViewSet, basename='lesson')
router.register(r'volunteer-roles', VolunteerRoleViewSet, basename='volunteer-role')

urlpatterns = [
    path('transcribe/', transcribe_audio, name='transcribe-audio'),
    path('lessons/<int:lesson_id>/transcribe/', transcribe_lesson_audio, name='transcribe-lesson'),
    path('', include(router.urls)),
]

