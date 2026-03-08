# دليل تصحيح مشكلة عدم ظهور الدرس

## خطوات التحقق:

### 1. التحقق من حالة الدرس في قاعدة البيانات:
```bash
python manage.py shell
```

```python
from lessons.models import Lesson
lessons = Lesson.objects.all()
for lesson in lessons:
    print(f"ID: {lesson.id}, Title: {lesson.title}, Status: {lesson.status}, Category: {lesson.category.name if lesson.category else 'None'}")
```

### 2. التحقق من API مباشرة:
افتح المتصفح واذهب إلى:
- `http://127.0.0.1:8000/api/lessons/` - جميع الدروس المنشورة
- `http://127.0.0.1:8000/api/lessons/?category=1` - دروس مادة معينة

### 3. التحقق من حالة الدرس:
- يجب أن تكون `status = 'published'` (منشور)
- يجب أن تكون `category.is_active = True` (المادة نشطة)

### 4. التحقق من Flutter:
- تأكد من أن API URL صحيح في `lib/config/app_config.dart`
- تحقق من السجلات في Flutter Console

## الحلول الشائعة:

### المشكلة: الدرس بحالة `draft`
**الحل:** غير الحالة إلى `published` في لوحة الإدارة

### المشكلة: المادة غير نشطة
**الحل:** تأكد من أن `category.is_active = True`

### المشكلة: API لا يعرض الدرس
**الحل:** تحقق من `get_queryset()` في `LessonViewSet`
