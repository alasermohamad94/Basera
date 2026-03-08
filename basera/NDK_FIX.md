# حل مشكلة NDK

المشكلة: Flutter يطالب بـ NDK (Native Development Kit) غير مثبت.

## الحل السريع (المُوصى به)

### الطريقة 1: تثبيت NDK من Android Studio

1. افتح Android Studio
2. اذهب إلى **Tools** → **SDK Manager**
3. في تبويب **SDK Tools**، فعّل:
   - ✅ **NDK (Side by side)**
   - ✅ **CMake**
4. اضغط **Apply** وانتظر التثبيت
5. أعد تشغيل `flutter run`

### الطريقة 2: تثبيت NDK من سطر الأوامر

```bash
# في Windows PowerShell
cd $env:LOCALAPPDATA\Android\Sdk\cmdline-tools\latest\bin
.\sdkmanager.bat "ndk;27.0.12077973"
```

### الطريقة 3: جعل NDK اختياري (قد لا يعمل مع جميع الإصدارات)

في ملف `android/app/build.gradle.kts`، أضف:

```kotlin
android {
    // ... existing code ...
    
    defaultConfig {
        // ... existing code ...
        
        // Skip NDK if not needed
        externalNativeBuild {
            cmake {
                // Empty - no native code
            }
        }
    }
}
```

## ملاحظات

- NDK مطلوب عادة فقط للتطبيقات التي تستخدم native code (C/C++)
- معظم تطبيقات Flutter لا تحتاج NDK
- إذا استمرت المشكلة، تأكد من تحديث Flutter SDK:
  ```bash
  flutter upgrade
  ```

## البديل المؤقت

يمكنك محاولة تشغيل التطبيق بدون NDK عن طريق تعديل `build.gradle.kts`:

```kotlin
android {
    // ... existing code ...
    
    // Comment out or remove this line if it exists:
    // ndkVersion = flutter.ndkVersion
}
```

