# بنية المشروع - بصيرة

## 📁 هيكل المشروع

```
basera/
├── backend/                      # Django Backend
│   ├── basera_backend/          # إعدادات Django الرئيسية
│   │   ├── settings.py          # إعدادات المشروع
│   │   ├── urls.py              # URLs الرئيسية
│   │   ├── wsgi.py              # WSGI config
│   │   └── asgi.py              # ASGI config
│   ├── core/                    # تطبيق المستخدمين
│   │   ├── models.py            # نموذج User
│   │   ├── views.py             # APIs للمصادقة
│   │   ├── serializers.py       # Serializers
│   │   └── urls.py              # URLs للمصادقة
│   ├── lessons/                 # تطبيق الدروس
│   │   ├── models.py            # Category, Lesson, LessonSection, LessonProgress
│   │   ├── views.py             # APIs للدروس
│   │   ├── serializers.py       # Serializers
│   │   └── urls.py              # URLs للدروس
│   ├── tests/                   # تطبيق الاختبارات
│   │   ├── models.py            # Quiz, Question, Choice, QuizAttempt, Answer
│   │   ├── views.py             # APIs للاختبارات
│   │   ├── serializers.py       # Serializers
│   │   └── urls.py              # URLs للاختبارات
│   ├── volunteers/              # تطبيق المتطوعين
│   │   ├── models.py            # TranscriptionReview, AudioRecording
│   │   ├── views.py             # APIs للمتطوعين
│   │   ├── serializers.py       # Serializers
│   │   └── urls.py              # URLs للمتطوعين
│   ├── manage.py                # Django management script
│   ├── requirements.txt         # Python dependencies
│   └── README.md                # وثائق Backend
│
├── lib/                         # Flutter Frontend
│   ├── main.dart                # نقطة الدخول
│   ├── config/
│   │   └── app_config.dart      # إعدادات التطبيق
│   ├── models/                  # Data Models
│   │   ├── user.dart            # نموذج المستخدم
│   │   ├── category.dart        # نموذج التصنيف
│   │   ├── lesson.dart          # نموذج الدرس
│   │   └── quiz.dart            # نموذج الاختبار
│   ├── services/                # Business Logic
│   │   ├── api_service.dart     # خدمة HTTP
│   │   ├── auth_service.dart    # خدمة المصادقة
│   │   ├── lesson_service.dart  # خدمة الدروس
│   │   ├── speech_service.dart  # Speech-to-Text & TTS
│   │   ├── voice_command_service.dart  # الأوامر الصوتية
│   │   └── accessibility_service.dart  # إمكانية الوصول
│   ├── screens/                 # UI Screens
│   │   ├── login_screen.dart    # شاشة تسجيل الدخول
│   │   ├── home_screen.dart     # الصفحة الرئيسية
│   │   ├── category_lessons_screen.dart  # دروس التصنيف
│   │   └── lesson_detail_screen.dart     # تفاصيل الدرس
│   └── widgets/                 # Reusable Widgets
│       ├── accessible_button.dart        # زر قابل للوصول
│       └── accessible_list_tile.dart     # قائمة قابلة للوصول
│
├── pubspec.yaml                 # Flutter dependencies
├── README.md                    # الوثائق الرئيسية
├── SETUP.md                     # دليل الإعداد
└── PROJECT_STRUCTURE.md         # هذا الملف
```

## 🔗 API Endpoints

### Authentication
- `POST /api/auth/register/` - تسجيل حساب جديد
- `POST /api/auth/login/` - تسجيل الدخول
- `GET /api/auth/profile/` - الملف الشخصي

### Lessons
- `GET /api/lessons/categories/` - قائمة التصنيفات
- `GET /api/lessons/` - قائمة الدروس
- `GET /api/lessons/{id}/` - تفاصيل الدرس
- `POST /api/lessons/{id}/update_progress/` - تحديث التقدم
- `GET /api/lessons/search/?q={query}` - البحث

### Tests
- `GET /api/tests/` - قائمة الاختبارات
- `GET /api/tests/{id}/` - تفاصيل الاختبار
- `POST /api/tests/{id}/start_attempt/` - بدء محاولة
- `POST /api/tests/{id}/submit_answer/` - تقديم إجابة
- `POST /api/tests/{id}/submit_attempt/` - إنهاء الاختبار

### Volunteers
- `GET /api/volunteers/transcriptions/` - المراجعات
- `POST /api/volunteers/transcriptions/` - إنشاء مراجعة
- `GET /api/volunteers/recordings/` - التسجيلات
- `POST /api/volunteers/recordings/` - رفع تسجيل

## 📊 Database Models

### Core
- **User**: المستخدمون (طالب، متطوع، مدير)

### Lessons
- **Category**: تصنيفات الدروس
- **Lesson**: الدروس
- **LessonSection**: أقسام الدرس (فقرات، عناوين)
- **LessonProgress**: تقدم المستخدم

### Tests
- **Quiz**: الاختبارات
- **Question**: الأسئلة
- **Choice**: خيارات الإجابة
- **QuizAttempt**: محاولات الاختبار
- **Answer**: الإجابات

### Volunteers
- **TranscriptionReview**: مراجعات التفريغ
- **AudioRecording**: التسجيلات الصوتية

## 🎯 الميزات المطبقة

✅ Backend API كامل  
✅ Flutter UI الأساسي  
✅ Speech-to-Text  
✅ Text-to-Speech  
✅ التنقل الصوتي  
✅ دعم Accessibility  
✅ مكتبة الدروس  
✅ نظام الاختبارات  
✅ نظام المتطوعين  

## 🔜 الميزات المستقبلية

- [ ] تحسين التفريغ الصوتي (Whisper integration)
- [ ] التلخيص الذكي (AI Summarization)
- [ ] دعم العمل بدون إنترنت الكامل
- [ ] إحصائيات التقدم المتقدمة
- [ ] نظام الإشعارات
- [ ] دعم متعدد اللغات

