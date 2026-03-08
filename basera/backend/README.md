# بصيرة - Backend API

Backend API لتطبيق بصيرة التعليمي للمكفوفين.

## الإعداد السريع

```bash
# إنشاء بيئة افتراضية
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

# تثبيت المتطلبات
pip install -r requirements.txt

# إعداد قاعدة البيانات
python manage.py makemigrations
python manage.py migrate

# إنشاء مستخدم إداري
python manage.py createsuperuser

# تشغيل السيرفر
python manage.py runserver
```

## API Endpoints

### Authentication
- `POST /api/auth/register/` - إنشاء حساب جديد
- `POST /api/auth/login/` - تسجيل الدخول
- `GET /api/auth/profile/` - الحصول على الملف الشخصي

### Lessons
- `GET /api/lessons/categories/` - قائمة التصنيفات
- `GET /api/lessons/` - قائمة الدروس
- `GET /api/lessons/{id}/` - تفاصيل الدرس
- `POST /api/lessons/{id}/update_progress/` - تحديث التقدم
- `GET /api/lessons/search/?q={query}` - البحث في الدروس

### Tests
- `GET /api/tests/` - قائمة الاختبارات
- `GET /api/tests/{id}/` - تفاصيل الاختبار
- `POST /api/tests/{id}/start_attempt/` - بدء محاولة اختبار
- `POST /api/tests/{id}/submit_answer/` - تقديم إجابة
- `POST /api/tests/{id}/submit_attempt/` - إنهاء الاختبار

### Volunteers
- `GET /api/volunteers/transcriptions/` - قائمة المراجعات
- `POST /api/volunteers/transcriptions/` - إنشاء مراجعة
- `GET /api/volunteers/recordings/` - قائمة التسجيلات
- `POST /api/volunteers/recordings/` - رفع تسجيل جديد

## النماذج (Models)

### User
- `id`, `username`, `email`, `user_type` (student/volunteer/admin)
- `phone_number`, `date_joined`

### Category
- `id`, `name`, `description`, `icon`

### Lesson
- `id`, `title`, `description`, `category`
- `audio_file`, `transcribed_text`, `duration`
- `status`, `summary`, `sections`

### Quiz & Questions
- `Quiz`: `title`, `lesson`, `passing_score`
- `Question`: `question_type`, `question_text`, `choices`
- `QuizAttempt`: `user`, `quiz`, `score`, `passed`

## التطوير

```bash
# تشغيل الاختبارات
python manage.py test

# إنشاء migrations جديدة
python manage.py makemigrations

# تطبيق migrations
python manage.py migrate

# الوصول إلى admin panel
python manage.py runserver
# ثم زيارة http://localhost:8000/admin
```
