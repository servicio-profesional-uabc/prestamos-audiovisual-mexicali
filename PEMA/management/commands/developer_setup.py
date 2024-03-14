from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.conf import settings


class Command(BaseCommand):
    """
    *NO usar en producción*
    Crea un superusuario de prueba con nombre y contraseña 'admin' y '123'
    """

    SUPERUSER_NAME = 'admin'
    SUPERUSER_PASSWORD = '123'

    class ErrorMessages:
        ENVIRONMENT = 'No se puede ejecutar este comando en entornos de producción'

    def handle(self, **options):
        if not settings.DEBUG:
            self.stdout.write(self.style.ERROR(Command.ErrorMessages.ENVIRONMENT))
            return

        user = User.objects.create_user(
            username=Command.SUPERUSER_NAME,
            password=Command.SUPERUSER_PASSWORD,
        )

        user.is_superuser = True
        user.is_staff = True

        user.save()
