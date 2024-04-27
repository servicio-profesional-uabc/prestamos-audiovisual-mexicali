from django.apps import AppConfig


class PemaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'PEMA'

    def ready(self):
        import PEMA.signals