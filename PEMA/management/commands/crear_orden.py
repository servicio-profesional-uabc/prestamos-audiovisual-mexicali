from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from PEMA.models import Prestatario, Orden, Materia, EstadoOrden, TipoOrden
from django.utils.timezone import make_aware
from datetime import datetime
from django.conf import settings


class Command(BaseCommand):
    """
    *NO usar en producción*
    Crea ordenes de diferentes estados y usuario para el usuario 117 con password 123
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

        materia2 = Materia.objects.create(
            nombre='Iluminacion',
            periodo='2024-1',
        )

        # ordenes
        orden1 = Orden.objects.create(
            prestatario=user,
            nombre="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            lugar=Orden.Ubicacion.CAMPUS,
            inicio=make_aware(datetime(2024, 10, 5)),
            final=make_aware(datetime(2024, 10, 5)),
            estado=EstadoOrden.PENDIENTE_AP,
            materia=materia1,
        )

        orden2 = Orden.objects.create(
            prestatario=user,
            nombre="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            lugar=Orden.Ubicacion.EXTERNO,
            tipo=TipoOrden.EXTRAORDINARIA,
            inicio=make_aware(datetime(2024, 10, 5)),
            final=make_aware(datetime(2024, 10, 5)),
            estado=EstadoOrden.PENDIENTE_CR,
            materia=materia1,
            descripcion="Esta solicitud es para mi practica de Cinematografia en la laguna salada."
        )

        orden3 = Orden.objects.create(
            prestatario=user,
            nombre="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            lugar=Orden.Ubicacion.CAMPUS,
            inicio=make_aware(datetime(2024, 10, 5)),
            final=make_aware(datetime(2024, 10, 5)),
            estado=EstadoOrden.APROBADA,
            materia=materia2,
        )

        orden4 = Orden.objects.create(
            prestatario=user,
            nombre="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            lugar=Orden.Ubicacion.CAMPUS,
            inicio=make_aware(datetime(2024, 10, 5)),
            final=make_aware(datetime(2024, 10, 5)),
            estado=EstadoOrden.CANCELADA,
            materia=materia2,
        )

        orden5 = Orden.objects.create(
            prestatario=user,
            nombre="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            lugar=Orden.Ubicacion.CAMPUS,
            inicio=make_aware(datetime(2024, 10, 5)),
            final=make_aware(datetime(2024, 10, 5)),
            estado=EstadoOrden.RECHAZADA,
            materia=materia1,
        )

        orden6 = Orden.objects.create(
            prestatario=user,
            nombre="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            lugar=Orden.Ubicacion.CAMPUS,
            inicio=make_aware(datetime(2024, 10, 5)),
            final=make_aware(datetime(2024, 10, 5)),
            estado=EstadoOrden.APROBADA,
            materia=materia1,
        )

        user.is_superuser = False
        user.is_staff = False

        user.save()
        print('Se guardo usuario...')
        materia1.save()
        materia2.save()
        print('Se guardaron las materias...')
        orden1.save()
        orden2.save()
        orden3.save()
        orden4.save()
        orden5.save()
        orden6.save()
        print('Se guardaron las ordenes...')

