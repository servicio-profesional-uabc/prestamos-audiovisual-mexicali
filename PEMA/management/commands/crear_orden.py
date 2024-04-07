from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from PEMA.models import Prestatario, Orden, Materia
from django.utils.timezone import make_aware
from datetime import datetime
from django.conf import settings


class Command(BaseCommand):
    """
    *NO usar en producción*
    Crea una orden y usuario para el usuario 1234 con password 123
    """

    USERNAME = '117'
    PASSWORD = '123'

    class ErrorMessages:
        ENVIRONMENT = 'No se puede ejecutar este comando en entornos de producción'

    def handle(self, **options):
        if not settings.DEBUG:
            self.stdout.write(self.style.ERROR(Command.ErrorMessages.ENVIRONMENT))
            return

        user = Prestatario.crear_usuario(id=117, username=self.USERNAME, password=self.PASSWORD)

        # materias
        materia1 = Materia.objects.create(
            nombre='Cinematografia',
            periodo='2024-1',
        )

        # ordenes
        orden1 = Orden.objects.create(
            prestatario=user,
            lugar=Orden.Ubicacion.CAMPUS,
            inicio=make_aware(datetime(2024, 10, 5)),
            final=make_aware(datetime(2024, 10, 5)),
            estado=Orden.Estado.PENDIENTE_AP,
            materia=materia1,
        )

        user.is_superuser = False
        user.is_staff = False

        user.save()
        print('Se guardo usuario...')
        materia1.save()
        print('Se guardo materia...')
        orden1.save()
        print('Se guardo orden...')

