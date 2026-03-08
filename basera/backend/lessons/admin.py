from django.contrib import admin
from .models import (
    Grade, Category, Lesson, LessonSection, LessonProgress,
    Quiz, Question, QuestionChoice, QuizAttempt, Answer, VolunteerRole
)


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['name', 'subjects_count', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['order', 'name']
    list_editable = ['order', 'is_active']
    
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('name', 'description')
        }),
        ('الإعدادات', {
            'fields': ('order', 'is_active')
        }),
        ('معلومات النظام', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def subjects_count(self, obj):
        return obj.subjects_count
    subjects_count.short_description = 'عدد المواد'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_grade', 'lessons_count', 'order', 'is_active', 'created_at']
    list_filter = ['grade', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['grade__order', 'order', 'name']
    list_editable = ['order', 'is_active']
    
    def get_grade(self, obj):
        return obj.grade.name if obj.grade else 'بدون صف'
    get_grade.short_description = 'الصف الدراسي'
    
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('grade', 'name', 'description')
        }),
        ('الإعدادات', {
            'fields': ('icon', 'order', 'is_active')
        }),
        ('معلومات النظام', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def lessons_count(self, obj):
        return obj.lessons_count
    lessons_count.short_description = 'عدد الدروس'


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'status', 'conversion_status', 'conversion_progress', 'created_by', 'created_at']
    list_filter = ['status', 'category', 'conversion_status', 'created_at']
    search_fields = ['title', 'description', 'transcribed_text']
    readonly_fields = ['created_at', 'updated_at', 'conversion_status', 'conversion_progress', 'conversion_error']
    
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('title', 'description', 'category', 'created_by', 'reviewed_by', 'status', 'duration', 'summary')
        }),
        ('محتوى الدرس', {
            'fields': ('audio_file', 'pdf_file', 'text_content', 'transcribed_text', 'transcribed_text_reviewed')
        }),
        ('حالة التحويل', {
            'fields': ('conversion_status', 'conversion_progress', 'conversion_error'),
            'classes': ('collapse',)
        }),
        ('معلومات الزمن', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(LessonSection)
class LessonSectionAdmin(admin.ModelAdmin):
    list_display = ['lesson', 'section_type', 'order']
    list_filter = ['section_type']
    ordering = ['lesson', 'order']


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'completed', 'listening_time_seconds', 'last_accessed']
    list_filter = ['completed', 'last_accessed']
    readonly_fields = ['created_at']


# نماذج الاختبارات
@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'quiz_type', 'status', 'created_by', 'created_at']
    list_filter = ['quiz_type', 'status', 'category', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('title', 'description', 'category', 'lesson', 'quiz_type', 'created_by', 'reviewed_by', 'status', 'is_active')
        }),
        ('إعدادات الاختبار', {
            'fields': ('duration_minutes', 'passing_score', 'max_attempts')
        }),
        ('معلومات الزمن', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )


class QuestionChoiceInline(admin.TabularInline):
    model = QuestionChoice
    extra = 2


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'quiz', 'question_type', 'order', 'points']
    list_filter = ['question_type', 'quiz']
    search_fields = ['question_text']
    ordering = ['quiz', 'order']
    inlines = [QuestionChoiceInline]
    
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('quiz', 'question_text', 'question_type', 'order', 'points')
        }),
        ('الإجابة الصحيحة', {
            'fields': ('correct_answer',),
            'description': 'للأسئلة المفتوحة، اتركها فارغة للتصحيح اليدوي'
        }),
    )


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'quiz', 'status', 'score', 'percentage', 'passed', 'started_at']
    list_filter = ['status', 'passed', 'quiz', 'started_at']
    search_fields = ['user__username', 'quiz__title']
    readonly_fields = ['started_at', 'completed_at', 'time_taken_minutes']
    
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('user', 'quiz', 'status', 'reviewed_by', 'reviewed_at')
        }),
        ('النتائج', {
            'fields': ('score', 'total_points', 'percentage', 'passed', 'time_taken_minutes')
        }),
        ('المراجعة', {
            'fields': ('volunteer_feedback',),
            'description': 'ملاحظات المتطوع للأسئلة المفتوحة'
        }),
        ('التوقيت', {
            'fields': ('started_at', 'completed_at'),
        }),
    )


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['attempt', 'question', 'is_correct', 'points_earned', 'needs_review']
    list_filter = ['is_correct', 'needs_review', 'question__question_type']
    search_fields = ['attempt__user__username', 'question__question_text']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('attempt', 'question')
        }),
        ('الإجابة', {
            'fields': ('answer_text', 'selected_choice', 'answer_audio')
        }),
        ('النتيجة', {
            'fields': ('is_correct', 'points_earned', 'needs_review', 'reviewed_by')
        }),
        ('معلومات النظام', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(VolunteerRole)
class VolunteerRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'category', 'tasks_completed', 'is_active', 'assigned_at']
    list_filter = ['role', 'is_active', 'category']
    search_fields = ['user__username', 'category__name']
    readonly_fields = ['assigned_at']
    
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('user', 'role', 'category')
        }),
        ('الإحصائيات', {
            'fields': ('tasks_completed', 'tasks_in_progress')
        }),
        ('الحالة', {
            'fields': ('is_active', 'assigned_at')
        }),
    )

