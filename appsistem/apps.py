from django.apps import AppConfig

class AppsistemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'appsistem'

    def ready(self):
        from . import signals  # noqa