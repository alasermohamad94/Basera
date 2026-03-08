from django.db import models
from django.contrib.auth import get_user_model
from lessons.models import Lesson

User = get_user_model()


class Quiz(models.Model):
    """نموذج الاختبار"""
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='quizzes', verbose_name='الدرس')
    title = models.CharField(max_length=300, verbose_name='العنوان')
    description = models.TextField(blank=True, null=True, verbose_name='الوصف')
    passing_score = models.IntegerField(default=70, verbose_name='نقاط النجاح')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'اختبار'
        verbose_name_plural = 'الاختبارات'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.lesson.title} - {self.title}"


class Question(models.Model):
    """سؤال في الاختبار"""
    QUESTION_TYPES = [
        ('multiple_choice', 'اختيار من متعدد'),
        ('true_false', 'صحيح/خطأ'),
        ('text_answer', 'إجابة نصية'),
        ('audio_answer', 'إجابة صوتية'),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions', verbose_name='الاختبار')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='multiple_choice', verbose_name='نوع السؤال')
    question_text = models.TextField(verbose_name='نص السؤال')
    question_audio = models.FileField(upload_to='questions/audio/', blank=True, null=True, verbose_name='صوت السؤال')
    order = models.IntegerField(default=0, verbose_name='الترتيب')
    points = models.IntegerField(default=1, verbose_name='النقاط')

    class Meta:
        verbose_name = 'سؤال'
        verbose_name_plural = 'الأسئلة'
        ordering = ['order']

    def __str__(self):
        return self.question_text[:50]


class Choice(models.Model):
    """خيارات الإجابة (للأسئلة متعددة الاختيارات)"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices', verbose_name='السؤال')
    choice_text = models.TextField(verbose_name='نص الخيار')
    is_correct = models.BooleanField(default=False, verbose_name='صحيح')

    class Meta:
        verbose_name = 'خيار'
        verbose_name_plural = 'خيارات'

    def __str__(self):
        return self.choice_text[:50]


class QuizAttempt(models.Model):
    """محاولة إجراء الاختبار"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts', verbose_name='المستخدم')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts', verbose_name='الاختبار')
    score = models.FloatField(default=0, verbose_name='النتيجة')
    passed = models.BooleanField(default=False, verbose_name='نجح')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'محاولة اختبار'
        verbose_name_plural = 'محاولات الاختبارات'
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title}"


class Answer(models.Model):
    """إجابة على سؤال"""
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers', verbose_name='المحاولة')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='السؤال')
    answer_text = models.TextField(blank=True, null=True, verbose_name='الإجابة النصية')
    answer_audio = models.FileField(upload_to='answers/audio/', blank=True, null=True, verbose_name='الإجابة الصوتية')
    selected_choice = models.ForeignKey(Choice, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='الخيار المختار')
    is_correct = models.BooleanField(default=False, verbose_name='صحيح')
    points_earned = models.FloatField(default=0, verbose_name='النقاط المكتسبة')
    reviewed = models.BooleanField(default=False, verbose_name='تمت المراجعة')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='reviewed_answers', verbose_name='راجع بواسطة')

    class Meta:
        verbose_name = 'إجابة'
        verbose_name_plural = 'الإجابات'

    def __str__(self):
        return f"{self.attempt.user.username} - {self.question.question_text[:30]}"

