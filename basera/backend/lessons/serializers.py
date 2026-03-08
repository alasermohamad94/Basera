from rest_framework import serializers
from .models import (
    Grade, Category, Lesson, LessonSection, LessonProgress,
    Quiz, Question, QuestionChoice, QuizAttempt, Answer, VolunteerRole
)


class GradeSerializer(serializers.ModelSerializer):
    subjects_count = serializers.SerializerMethodField()

    class Meta:
        model = Grade
        fields = ['id', 'name', 'description', 'subjects_count', 'order', 'is_active', 'created_at']

    def get_subjects_count(self, obj):
        return obj.subjects_count


class CategorySerializer(serializers.ModelSerializer):
    grade_name = serializers.SerializerMethodField()
    grade_id = serializers.SerializerMethodField()
    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'grade', 'grade_id', 'grade_name', 'name', 'description', 
                  'icon', 'lessons_count', 'order', 'is_active', 'created_at']

    def get_grade_name(self, obj):
        return obj.grade.name if obj.grade else None
    
    def get_grade_id(self, obj):
        return obj.grade.id if obj.grade else None

    def get_lessons_count(self, obj):
        return obj.lessons_count


class LessonSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonSection
        fields = ['id', 'section_type', 'text', 'order', 'audio_timestamp']


class LessonSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    sections = LessonSectionSerializer(many=True, read_only=True)
    audio_file_url = serializers.SerializerMethodField()
    pdf_file_url = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'category', 'category_name',
                  'audio_file', 'audio_file_url', 'pdf_file', 'pdf_file_url',
                  'text_content', 'transcribed_text',
                  'transcribed_text_reviewed', 'duration', 'status',
                  'summary', 'sections', 'created_by', 'created_at',
                  'updated_at', 'published_at',
                  'conversion_status', 'conversion_progress', 'conversion_error']

    def get_category_name(self, obj):
        return obj.category.name if obj.category else None
    
    def get_audio_file_url(self, obj):
        if obj.audio_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.audio_file.url)
        return None
    
    def get_pdf_file_url(self, obj):
        if obj.pdf_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.pdf_file.url)
        return None


class LessonProgressSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)

    class Meta:
        model = LessonProgress
        fields = ['id', 'user', 'lesson', 'lesson_title', 'completed',
                  'current_position', 'listening_time_seconds', 'last_accessed', 'created_at']
        read_only_fields = ['user']


# Serializers للاختبارات
class QuestionChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionChoice
        fields = ['id', 'choice_text', 'order', 'is_correct']


class QuestionSerializer(serializers.ModelSerializer):
    choices = QuestionChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'question_text', 'question_type', 'order', 'points',
                  'correct_answer', 'choices']


class QuizSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    questions_count = serializers.IntegerField(read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'category', 'category_name',
                  'lesson', 'lesson_title', 'quiz_type', 'duration_minutes',
                  'passing_score', 'max_attempts', 'status', 'is_active',
                  'questions_count', 'questions', 'created_by', 'created_at',
                  'updated_at', 'published_at']


class AnswerSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.question_text', read_only=True)
    question_type = serializers.CharField(source='question.question_type', read_only=True)

    class Meta:
        model = Answer
        fields = ['id', 'question', 'question_text', 'question_type',
                  'answer_text', 'selected_choice', 'answer_audio',
                  'is_correct', 'points_earned', 'needs_review',
                  'reviewed_by', 'created_at']


class QuizAttemptSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = QuizAttempt
        fields = ['id', 'user', 'quiz', 'quiz_title', 'status',
                  'score', 'total_points', 'percentage', 'passed',
                  'started_at', 'completed_at', 'time_taken_minutes',
                  'volunteer_feedback', 'reviewed_by', 'reviewed_at', 'answers']
        read_only_fields = ['user']


class VolunteerRoleSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    role_display = serializers.SerializerMethodField()

    class Meta:
        model = VolunteerRole
        fields = ['id', 'user', 'user_username', 'role', 'role_display',
                  'category', 'category_name', 'tasks_completed',
                  'tasks_in_progress', 'is_active', 'assigned_at']
    
    def get_role_display(self, obj):
        return obj.get_role_display()

