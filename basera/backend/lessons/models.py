from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Grade(models.Model):
    """الصفوف الدراسية (مثل: صف تاسع، صف ثامن)"""
    name = models.CharField(max_length=200, verbose_name='اسم الصف')
    description = models.TextField(blank=True, null=True, verbose_name='الوصف')
    order = models.IntegerField(default=0, verbose_name='ترتيب العرض')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'صف دراسي'
        verbose_name_plural = 'الصفوف الدراسية'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name
    
    @property
    def subjects_count(self):
        """عدد المواد في هذا الصف"""
        return self.subjects.filter(is_active=True).count()


class Category(models.Model):
    """المواد الدراسية (مثل: الرياضيات، اللغة العربية)"""
    grade = models.ForeignKey(
        Grade, 
        on_delete=models.CASCADE, 
        related_name='subjects',
        verbose_name='الصف الدراسي',
        null=True,
        blank=True
    )
    name = models.CharField(max_length=200, verbose_name='اسم المادة')
    description = models.TextField(blank=True, null=True, verbose_name='الوصف')
    icon = models.CharField(max_length=100, blank=True, null=True, verbose_name='أيقونة')
    order = models.IntegerField(default=0, verbose_name='ترتيب العرض')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'مادة دراسية'
        verbose_name_plural = 'المواد الدراسية'
        ordering = ['grade__order', 'order', 'name']
        # unique_together = [['grade', 'name']]  # تم التعليق عليها للسماح بالمواد بدون صف مؤقتاً

    def __str__(self):
        if self.grade:
            return f"{self.grade.name} - {self.name}"
        return self.name
    
    @property
    def lessons_count(self):
        """عدد الدروس المنشورة في هذه المادة"""
        return self.lessons.filter(status='published').count()


class Lesson(models.Model):
    """نموذج الدرس"""
    STATUS_CHOICES = [
        ('draft', 'مسودة'),
        ('review', 'قيد المراجعة'),
        ('approved', 'معتمد'),
        ('published', 'منشور'),
    ]

    title = models.CharField(max_length=300, verbose_name='عنوان الدرس')
    description = models.TextField(blank=True, null=True, verbose_name='الوصف')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='lessons', verbose_name='المادة الدراسية')
    
    # ملفات صوتية
    audio_file = models.FileField(upload_to='lessons/audio/', blank=True, null=True, verbose_name='الملف الصوتي')
    
    # ملفات PDF والنص الأصلي
    pdf_file = models.FileField(upload_to='lessons/pdf/', blank=True, null=True, verbose_name='ملف PDF')
    text_content = models.TextField(blank=True, null=True, verbose_name='محتوى النص')
    
    # النص المفروغ
    transcribed_text = models.TextField(blank=True, null=True, verbose_name='النص المفروغ')
    transcribed_text_reviewed = models.BooleanField(default=False, verbose_name='تمت مراجعة النص')
    
    # حالة التحويل (للتتبع)
    CONVERSION_STATUS_CHOICES = [
        ('idle', 'في الانتظار'),
        ('extracting_text', 'جاري استخراج النص'),
        ('text_extracted', 'تم استخراج النص'),
        ('converting_audio', 'جاري تحويل النص إلى صوت'),
        ('completed', 'اكتمل'),
        ('failed', 'فشل'),
    ]
    conversion_status = models.CharField(
        max_length=20, 
        choices=CONVERSION_STATUS_CHOICES, 
        default='idle', 
        verbose_name='حالة التحويل'
    )
    conversion_progress = models.IntegerField(default=0, verbose_name='نسبة التقدم (%)')
    conversion_error = models.TextField(blank=True, null=True, verbose_name='خطأ التحويل')
    
    # معلومات إضافية
    duration = models.IntegerField(default=0, verbose_name='المدة بالثواني')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='الحالة')
    
    # معلومات منشئ الدرس
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_lessons', verbose_name='أنشئ بواسطة')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_lessons', verbose_name='راجع بواسطة')
    
    # ملخص ذكي
    summary = models.TextField(blank=True, null=True, verbose_name='الملخص')
    
    # معلومات الزمن
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'درس'
        verbose_name_plural = 'الدروس'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class LessonSection(models.Model):
    """أقسام الدرس (فقرات، عناوين، نقاط)"""
    SECTION_TYPES = [
        ('paragraph', 'فقرة'),
        ('heading', 'عنوان'),
        ('point', 'نقطة'),
    ]

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='sections', verbose_name='الدرس')
    section_type = models.CharField(max_length=20, choices=SECTION_TYPES, default='paragraph', verbose_name='نوع القسم')
    text = models.TextField(verbose_name='النص')
    order = models.IntegerField(default=0, verbose_name='الترتيب')
    audio_timestamp = models.FloatField(blank=True, null=True, verbose_name='وقت الصوت بالثواني')

    class Meta:
        verbose_name = 'قسم الدرس'
        verbose_name_plural = 'أقسام الدروس'
        ordering = ['order']

    def __str__(self):
        return f"{self.lesson.title} - {self.get_section_type_display()}"


class LessonProgress(models.Model):
    """تتبع تقدم المستخدم في الدروس"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_progress', verbose_name='المستخدم')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress', verbose_name='الدرس')
    completed = models.BooleanField(default=False, verbose_name='مكتمل')
    current_position = models.FloatField(default=0, verbose_name='الموضع الحالي بالثواني')
    listening_time_seconds = models.IntegerField(default=0, verbose_name='وقت الاستماع بالثواني')
    last_accessed = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'تقدم الدرس'
        verbose_name_plural = 'تقدم الدروس'
        unique_together = ['user', 'lesson']

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title}"


class Quiz(models.Model):
    """نموذج الاختبار الصوتي"""
    TYPE_CHOICES = [
        ('practice', 'تمرين'),
        ('exam', 'امتحان'),
        ('quiz', 'اختبار قصير'),
    ]
    
    title = models.CharField(max_length=300, verbose_name='عنوان الاختبار')
    description = models.TextField(blank=True, null=True, verbose_name='الوصف')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='quizzes', verbose_name='المادة الدراسية')
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True, related_name='lesson_quizzes', verbose_name='الدرس المرتبط')
    quiz_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='practice', verbose_name='نوع الاختبار')
    
    # إعدادات الاختبار
    duration_minutes = models.IntegerField(default=60, verbose_name='المدة بالدقائق')
    passing_score = models.IntegerField(default=60, verbose_name='نقاط النجاح')
    max_attempts = models.IntegerField(default=3, verbose_name='الحد الأقصى للمحاولات')
    
    # حالة الاختبار
    status = models.CharField(max_length=20, choices=Lesson.STATUS_CHOICES, default='draft', verbose_name='الحالة')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    
    # معلومات منشئ الاختبار
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_quizzes', verbose_name='أنشئ بواسطة')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_quizzes', verbose_name='راجع بواسطة')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'اختبار'
        verbose_name_plural = 'الاختبارات'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def questions_count(self):
        """عدد الأسئلة في الاختبار"""
        return self.questions.count()


class Question(models.Model):
    """نموذج السؤال في الاختبار"""
    TYPE_CHOICES = [
        ('multiple_choice', 'اختيار من متعدد'),
        ('true_false', 'صحيح/خطأ'),
        ('open_ended', 'سؤال مفتوح'),
        ('voice_answer', 'إجابة صوتية'),
    ]
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions', verbose_name='الاختبار')
    question_text = models.TextField(verbose_name='نص السؤال')
    question_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='multiple_choice', verbose_name='نوع السؤال')
    order = models.IntegerField(default=0, verbose_name='الترتيب')
    points = models.IntegerField(default=1, verbose_name='النقاط')
    
    # للإجابات الصحيحة (للسؤال المفتوح يتم التصحيح اليدوي)
    correct_answer = models.TextField(blank=True, null=True, verbose_name='الإجابة الصحيحة')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'سؤال'
        verbose_name_plural = 'الأسئلة'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.quiz.title} - {self.question_text[:50]}"


class QuestionChoice(models.Model):
    """خيارات السؤال (لاختيار من متعدد)"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices', verbose_name='السؤال')
    choice_text = models.CharField(max_length=500, verbose_name='نص الخيار')
    order = models.IntegerField(default=0, verbose_name='الترتيب')
    is_correct = models.BooleanField(default=False, verbose_name='إجابة صحيحة')
    
    class Meta:
        verbose_name = 'خيار السؤال'
        verbose_name_plural = 'خيارات الأسئلة'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.question.question_text[:30]} - {self.choice_text}"


class QuizAttempt(models.Model):
    """محاولة الطالب في الاختبار"""
    STATUS_CHOICES = [
        ('in_progress', 'قيد التنفيذ'),
        ('completed', 'مكتمل'),
        ('timeout', 'انتهى الوقت'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_quiz_attempts', verbose_name='المستخدم')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts', verbose_name='الاختبار')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress', verbose_name='الحالة')
    
    # النتائج
    score = models.FloatField(default=0, verbose_name='الدرجة')
    total_points = models.IntegerField(default=0, verbose_name='إجمالي النقاط')
    percentage = models.FloatField(default=0, verbose_name='النسبة المئوية')
    passed = models.BooleanField(default=False, verbose_name='ناجح')
    
    # التوقيت
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='بدأ في')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='اكتمل في')
    time_taken_minutes = models.IntegerField(default=0, verbose_name='الوقت المستغرق بالدقائق')
    
    # ملاحظات المتطوع (للسؤال المفتوح)
    volunteer_feedback = models.TextField(blank=True, null=True, verbose_name='ملاحظات المتطوع')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_attempts', verbose_name='راجع بواسطة')
    reviewed_at = models.DateTimeField(blank=True, null=True, verbose_name='تمت المراجعة في')
    
    class Meta:
        verbose_name = 'محاولة الاختبار'
        verbose_name_plural = 'محاولات الاختبارات'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} - {self.status}"


class Answer(models.Model):
    """إجابة الطالب على سؤال"""
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers', verbose_name='المحاولة')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', verbose_name='السؤال')
    answer_text = models.TextField(blank=True, null=True, verbose_name='نص الإجابة')
    selected_choice = models.ForeignKey(QuestionChoice, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='الخيار المختار')
    answer_audio = models.FileField(upload_to='quizzes/audio_answers/', blank=True, null=True, verbose_name='إجابة صوتية')
    
    # التصحيح
    is_correct = models.BooleanField(default=False, verbose_name='إجابة صحيحة')
    points_earned = models.IntegerField(default=0, verbose_name='النقاط المكتسبة')
    
    # للمراجعة اليدوية
    needs_review = models.BooleanField(default=False, verbose_name='يحتاج مراجعة')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_lesson_answers', verbose_name='راجع بواسطة')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'إجابة'
        verbose_name_plural = 'الإجابات'
        unique_together = ['attempt', 'question']
    
    def __str__(self):
        return f"{self.attempt.user.username} - {self.question.question_text[:30]}"


class VolunteerRole(models.Model):
    """دور المتطوع في النظام"""
    ROLE_CHOICES = [
        ('reviewer', 'مراجع محتوى'),
        ('transcriber', 'مفروغ صوتي'),
        ('quiz_reviewer', 'مراجع اختبارات'),
        ('content_creator', 'منشئ محتوى'),
        ('admin', 'مدير'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='volunteer_roles', verbose_name='المستخدم')
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, verbose_name='الدور')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='volunteers', verbose_name='المادة (اختياري)')
    
    # الإحصائيات
    tasks_completed = models.IntegerField(default=0, verbose_name='المهام المكتملة')
    tasks_in_progress = models.IntegerField(default=0, verbose_name='المهام قيد التنفيذ')
    
    # الحالة
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    assigned_at = models.DateTimeField(auto_now_add=True, verbose_name='تم التعيين في')
    
    class Meta:
        verbose_name = 'دور المتطوع'
        verbose_name_plural = 'أدوار المتطوعين'
        unique_together = ['user', 'role', 'category']
    
    def __str__(self):
        role_name = dict(self.ROLE_CHOICES).get(self.role, self.role)
        if self.category:
            return f"{self.user.username} - {role_name} - {self.category.name}"
        return f"{self.user.username} - {role_name}"

