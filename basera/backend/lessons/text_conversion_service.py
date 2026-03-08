"""
خدمة لتحويل PDF والنص إلى نص مفروغ
"""
import os
import re
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    logger.warning("PyPDF2 غير مثبت. لن يعمل تحويل PDF.")

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    logger.warning("pdfplumber غير مثبت. لن يعمل تحويل PDF المحسن.")


class TextConversionService:
    """خدمة تحويل PDF والنص إلى نص مفروغ"""

    @staticmethod
    def _is_arabic_char(char):
        """التحقق من أن الحرف عربي"""
        return '\u0600' <= char <= '\u06FF' or '\u0750' <= char <= '\u077F' or \
               '\u08A0' <= char <= '\u08FF' or '\uFB50' <= char <= '\uFDFF' or \
               '\uFE70' <= char <= '\uFEFF'

    @staticmethod
    def _fix_arabic_direction(text):
        """
        تصحيح اتجاه النص العربي - إصلاح النص المعكوس
        
        المشكلة: بعض مكتبات استخراج PDF تستخرج النص العربي بشكل معكوس
        الحل: عكس الأحرف العربية في كل كلمة عربية
        
        Args:
            text: النص المراد تصحيحه
            
        Returns:
            str: النص المصحح
        """
        if not text:
            return ""
        
        # تقسيم النص إلى كلمات
        words = text.split()
        fixed_words = []
        
        for word in words:
            # التحقق من أن الكلمة تحتوي على أحرف عربية
            has_arabic = any(TextConversionService._is_arabic_char(char) for char in word)
            
            if has_arabic:
                # عكس الكلمة العربية (لإصلاح الاتجاه المعكوس)
                # لكن نحافظ على علامات الترقيم في نهاية الكلمة
                word_chars = list(word)
                # العثور على نهاية الحروف (بداية علامات الترقيم)
                end_punct = len(word_chars)
                for i in range(len(word_chars) - 1, -1, -1):
                    if TextConversionService._is_arabic_char(word_chars[i]) or word_chars[i].isalnum():
                        end_punct = i + 1
                        break
                
                # عكس الجزء العربي فقط
                if end_punct > 0:
                    arabic_part = word_chars[:end_punct]
                    punct_part = word_chars[end_punct:]
                    fixed_word = ''.join(reversed(arabic_part)) + ''.join(punct_part)
                else:
                    fixed_word = word
                
                fixed_words.append(fixed_word)
            else:
                # إذا لم تكن كلمة عربية، نتركها كما هي
                fixed_words.append(word)
        
        return ' '.join(fixed_words)

    @staticmethod
    def extract_text_from_pdf(pdf_file_path):
        """
        استخراج النص من ملف PDF

        Args:
            pdf_file_path: مسار ملف PDF

        Returns:
            str: النص المستخرج من PDF
        """
        if not os.path.exists(pdf_file_path):
            logger.error(f"ملف PDF غير موجود: {pdf_file_path}")
            return None

        text_content = ""

        # محاولة استخدام pdfplumber أولاً (أفضل للغة العربية)
        if PDFPLUMBER_AVAILABLE:
            try:
                with pdfplumber.open(pdf_file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_content += page_text + "\n\n"
                if text_content.strip():
                    logger.info(f"تم استخراج النص من PDF باستخدام pdfplumber ({len(text_content)} حرف)")
                    # تصحيح اتجاه النص العربي
                    fixed_text = TextConversionService._fix_arabic_direction(text_content.strip())
                    return fixed_text
            except Exception as e:
                logger.warning(f"فشل استخراج النص باستخدام pdfplumber: {e}")

        # استخدام PyPDF2 كبديل
        if PYPDF2_AVAILABLE:
            try:
                with open(pdf_file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_content += page_text + "\n\n"
                if text_content.strip():
                    logger.info(f"تم استخراج النص من PDF باستخدام PyPDF2 ({len(text_content)} حرف)")
                    # تصحيح اتجاه النص العربي
                    fixed_text = TextConversionService._fix_arabic_direction(text_content.strip())
                    return fixed_text
            except Exception as e:
                logger.error(f"فشل استخراج النص من PDF: {e}")

        logger.error("فشل استخراج النص من PDF. تأكد من تثبيت PyPDF2 أو pdfplumber.")
        return None

    @staticmethod
    def clean_text(text):
        """
        تنظيف النص من المسافات الزائدة والأحرف غير المرغوبة

        Args:
            text: النص المراد تنظيفه

        Returns:
            str: النص المنظف
        """
        if not text:
            return ""

        # إزالة المسافات الزائدة
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            cleaned_line = ' '.join(line.split())
            if cleaned_line.strip():
                cleaned_lines.append(cleaned_line)

        return '\n'.join(cleaned_lines)

    @staticmethod
    def process_lesson_text(lesson):
        """
        معالجة نص الدرس من PDF أو text_content

        Args:
            lesson: كائن Lesson

        Returns:
            str: النص المعالج أو None
        """
        # إذا كان هناك نص مباشر
        if lesson.text_content:
            cleaned_text = TextConversionService.clean_text(lesson.text_content)
            if cleaned_text:
                return cleaned_text

        # إذا كان هناك ملف PDF
        if lesson.pdf_file:
            pdf_path = lesson.pdf_file.path
            if os.path.exists(pdf_path):
                extracted_text = TextConversionService.extract_text_from_pdf(pdf_path)
                if extracted_text:
                    return TextConversionService.clean_text(extracted_text)

        return None