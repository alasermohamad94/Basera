# دليل الإعداد السريع - بصيرة

## الخطوات الأساسية

### 1. Backend Setup

```bash
cd backend

# إنشاء بيئة افتراضية
python -m venv venv

# تفعيل البيئة
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# تثبيت المتطلبات
pip install -r requirements.txt

# إعداد قاعدة البيانات
python manage.py makemigrations core lessons tests volunteers
python manage.py migrate

# إنشاء مستخدم إداري
python manage.py createsuperuser

# تشغيل السيرفر
python manage.py runserver
```

**مهم على Windows:** لا تستخدم `python` العام. فعّل بيئة المشروع أولاً:

```powershell
cd backend
.\venv\Scripts\activate
python manage.py runserver
```

أو شغّل مباشرة بدون تفعيل:

```powershell
cd backend
.\venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

أو انقر / نفّذ الملف: `backend\run_server.bat`

الـ API سيكون متاح على: `http://localhost:8000/api/`

### 2. Frontend Setup

```bash
# تثبيت المتطلبات
flutter pub get

# تشغيل التطبيق
flutter run
```

### 3. تحديث إعدادات API

في ملف `lib/config/app_config.dart`، تأكد من أن `baseUrl` يشير إلى عنوان السيرفر الصحيح:

```dart
static const String baseUrl = 'http://localhost:8000/api';
```

للأجهزة الحقيقية، استخدم عنوان IP لجهازك بدلاً من `localhost`:
```dart
static const String baseUrl = 'http://192.168.1.XXX:8000/api';
```

## ملاحظات مهمة

1. **الصلاحيات**: تأكد من منح صلاحيات الميكروفون والتخزين للتطبيق
2. **الإنترنت**: للاختبار المحلي، تأكد أن الجهاز والسيرفر على نفس الشبكة
3. **CORS**: تم تفعيل CORS في الـ backend للتطوير، تأكد من إعداده بشكل صحيح للإنتاج

## استكشاف الأخطاء

### Backend لا يعمل
- تأكد من تثبيت جميع المتطلبات: `pip install -r requirements.txt`
- تأكد من تشغيل migrations: `python manage.py migrate`
- تحقق من المنفذ 8000 غير مستخدم

### Flutter لا يتصل بالـ API
- تحقق من عنوان `baseUrl` في `app_config.dart`
- للأجهزة الحقيقية، استخدم IP address بدلاً من `localhost`
- تأكد من تشغيل السيرفر

### مشاكل الصوت
- تأكد من منح صلاحيات الميكروفون
- تحقق من إعدادات اللغة في الجهاز (العربية)
- للـ iOS، تأكد من إضافة وصف الصلاحيات في `Info.plist`

