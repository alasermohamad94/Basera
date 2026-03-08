# دليل التفريغ الصوتي التلقائي

## الميزة

التطبيق يدعم التفريغ الصوتي التلقائي للملفات الصوتية باستخدام Whisper AI.

## الإعداد

### 1. تثبيت المتطلبات

```bash
cd backend
pip install openai-whisper ffmpeg-python
```

### 2. تثبيت FFmpeg

**Windows:**
- تحميل من: https://ffmpeg.org/download.html
- إضافة إلى PATH

**Linux:**
```bash
sudo apt-get install ffmpeg
```

**Mac:**
```bash
brew install ffmpeg
```

### 3. استخدام API

#### رفع ملف صوتي وتفريغه:

```http
POST /api/lessons/transcribe/
Content-Type: multipart/form-data

audio_file: [ملف صوتي]
lesson_id: [اختياري] ID الدرس
```

#### تفريغ ملف صوتي لدرس موجود:

```http
POST /api/lessons/{lesson_id}/transcribe/
```

## استخدام من Flutter

### رفع ملف صوتي:

1. افتح شاشة "رفع وتفريغ درس جديد"
2. اضغط "اختر ملف صوتي"
3. اختر الملف من الجهاز
4. اضغط "تفريغ الملف الصوتي"
5. انتظر حتى يكتمل التفريغ
6. سيظهر النص المفروغ تلقائياً

### تفريغ درس موجود:

- يمكن تفريغ الملف الصوتي لدرس موجود من واجهة الإدارة

## ملاحظات

- النماذج المتاحة: tiny, base, small, medium, large
- النموذج الافتراضي: `base` (متوازن بين السرعة والدقة)
- للدقة الأعلى: استخدم `medium` أو `large`
- للسرعة الأعلى: استخدم `tiny` أو `base`

## بدائل Whisper

يمكن استخدام:
- Google Speech-to-Text API
- Azure Speech Services
- AWS Transcribe

للتبديل، عدّل `transcription_service.py`


