from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from PEMA.models import Almacen, Coordinador, Maestro, Prestatario


class Command(BaseCommand):
    """
    *NO usar en producción*
    Crea un superusuario de prueba con nombre y contraseña 'admin' y '123'
    """

    class ErrorMessages:
        ENVIRONMENT = 'No se puede ejecutar este comando en entornos de producción'

    def handle(self, **options):
        if not settings.DEBUG:
            self.stdout.write(self.style.ERROR(Command.ErrorMessages.ENVIRONMENT))
            return

        admin = User.objects.create_user(
            username='admin',
            password='123',
            is_superuser=True,
            is_staff=True
        )

        almacen = Almacen.crear_usuario(
            username='almacen',
            password='123',
            is_staff=True,
        )

        coordinador = Coordinador.crear_usuario(
            username='coordinador',
            password='123',
            is_staff=True,
        )

        maestro = Maestro.crear_usuario(
            username='maestro',
            password='123',
        )

        prestatario = Prestatario.crear_usuario(
            username='prestatario',
            password='123',
        )





