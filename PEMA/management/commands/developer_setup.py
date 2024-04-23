from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from PEMA.models import Almacen, Coordinador, Maestro, Prestatario


class Command(BaseCommand):
    """
    Este comando crea varios usuarios para diferentes roles en el sistema.
    *NO usar en producción*

    Este comando crea los siguientes usuarios:
    - Un superusuario administrativo con nombre de usuario 'admin' y contraseña '123'.
    - Un usuario de almacén con nombre de usuario 'almacen' y contraseña '123'.
    - Un usuario coordinador con nombre de usuario 'coordinador' y contraseña '123'.
    - Un usuario maestro con nombre de usuario 'maestro' y contraseña '123'.
    - Un usuario prestatario con nombre de usuario 'prestatario' y contraseña '123'.
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





