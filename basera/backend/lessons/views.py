from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from datetime import timedelta
from .models import (
    Grade, Category, Lesson, LessonProgress,
    VolunteerRole
)
from .serializers import (
    GradeSerializer, CategorySerializer, LessonSerializer, LessonProgressSerializer,
    VolunteerRoleSerializer
)


class GradeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Grade.objects.filter(is_active=True)
    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['order', 'name', 'created_at']
    ordering = ['order', 'name']
    
    @action(detail=True, methods=['get'])
    def subjects(self, request, pk=None):
        """الحصول على المواد الدراسية لصف معين"""
        grade = self.get_object()
        subjects = Category.objects.filter(grade=grade, is_active=True)
        serializer = CategorySerializer(subjects, many=True)
        return Response(serializer.data)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['grade']
    search_fields = ['name', 'description', 'grade__name']
    ordering_fields = ['order', 'name', 'created_at']
    ordering = ['grade__order', 'order', 'name']


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.filter(status='published')
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'status']
    search_fields = ['title', 'description', 'transcribed_text']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        # في حالة المستخدمين المميزين، يمكنهم رؤية الدروس غير المنشورة
        if self.request.user.is_authenticated and self.request.user.is_staff:
            queryset = Lesson.objects.all()
        return queryset

    @action(detail=True, methods=['get'])
    def conversion_status(self, request, pk=None):
        """الحصول على حالة تحويل الدرس"""
        lesson = self.get_object()
        return Response({
            'conversion_status': lesson.conversion_status,
            'conversion_progress': lesson.conversion_progress,
            'conversion_error': lesson.conversion_error,
        })

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def update_progress(self, request, pk=None):
        """تحديث تقدم المستخدم في الدرس"""
        lesson = self.get_object()
        current_position = request.data.get('current_position', 0)
        completed = request.data.get('completed', False)
        listening_time_seconds = request.data.get('listening_time_seconds', 0)

        progress, created = LessonProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson,
            defaults={
                'current_position': current_position,
                'completed': completed,
                'listening_time_seconds': listening_time_seconds
            }
        )

        if not created:
            progress.current_position = current_position
            progress.completed = completed
            progress.listening_time_seconds = listening_time_seconds
            progress.save()

        serializer = LessonProgressSerializer(progress)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def get_progress(self, request, pk=None):
        """الحصول على تقدم المستخدم في الدرس"""
        lesson = self.get_object()
        try:
            progress = LessonProgress.objects.get(user=request.user, lesson=lesson)
            serializer = LessonProgressSerializer(progress)
            return Response(serializer.data)
        except LessonProgress.DoesNotExist:
            return Response({
                'completed': False,
                'current_position': 0
            })

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def search(self, request):
        """البحث الصوتي في المحتوى"""
        query = request.query_params.get('q', '')
        if not query:
            return Response({'results': []})

        lessons = Lesson.objects.filter(
            transcribed_text__icontains=query,
            status='published'
        )[:20]

        serializer = self.get_serializer(lessons, many=True)
        return Response({'results': serializer.data})


class VolunteerRoleViewSet(viewsets.ModelViewSet):
    queryset = VolunteerRole.objects.filter(is_active=True)
    serializer_class = VolunteerRoleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # المستخدمون العاديون يرون فقط أدوارهم
        if not self.request.user.is_staff:
            return VolunteerRole.objects.filter(
                user=self.request.user,
                is_active=True
            )
        return VolunteerRole.objects.all()

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_roles(self, request):
        """الحصول على أدوار المستخدم"""
        roles = VolunteerRole.objects.filter(
            user=request.user,
            is_active=True
        )
        serializer = VolunteerRoleSerializer(roles, many=True)
        return Response(serializer.data)


