from django.apps import AppConfig


class LessonsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lessons'
    verbose_name = 'الدروس'

    def ready(self):
        """استيراد الإشارات عند تهيئة التطبيق"""
        import lessons.signals  # noqa

