# دليل الاتصال بين Flutter و Django

## إعدادات الاتصال

### للـ Android Emulator:
استخدم `http://10.0.2.2:8000/api` في `lib/config/app_config.dart`

### للأجهزة الحقيقية:
1. ابحث عن IP address لجهاز الكمبيوتر:
   - Windows: افتح PowerShell واكتب `ipconfig`
   - Linux/Mac: افتح Terminal واكتب `ifconfig` أو `ip addr`
   - ابحث عن `IPv4 Address` تحت `Wireless LAN adapter` أو `Ethernet adapter`

2. غير `baseUrl` في `lib/config/app_config.dart` إلى:
   ```dart
   static const String baseUrl = 'http://YOUR_IP_ADDRESS:8000/api';
   ```

3. تأكد من أن الكمبيوتر والجهاز/Emulator على نفس الشبكة (WiFi)

### تشغيل Django Server:
```bash
cd backend
python manage.py runserver 0.0.0.0:8000
```

**ملاحظة:** استخدم `0.0.0.0` بدلاً من `localhost` للسماح بالاتصال من الأجهزة الأخرى.

### تطبيق Migrations للـ Token Authentication:
```bash
cd backend
python manage.py migrate
```

## استكشاف الأخطاء

### خطأ "Connection refused":
- تأكد من أن Django server يعمل
- تأكد من استخدام `0.0.0.0:8000` وليس `localhost:8000`
- تأكد من أن IP address صحيح
- تأكد من أن Firewall لا يحظر المنفذ 8000

### خطأ CORS:
- تأكد من أن `CORS_ALLOW_ALL_ORIGINS = True` في `settings.py`
- تأكد من أن `django-cors-headers` مثبت

### خطأ Authentication:
- تأكد من تطبيق migrations بعد إضافة `rest_framework.authtoken`
- تأكد من أن Token يتم إنشاؤه عند تسجيل الدخول





