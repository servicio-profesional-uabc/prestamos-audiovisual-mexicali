from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from PEMA.models import Prestatario, Orden, Materia, Articulo, Unidad
from django.utils.timezone import make_aware
from datetime import datetime
from django.conf import settings


class Command(BaseCommand):
    """
    *NO usar en producción*
    Crea ordenes de diferentes estados y usuario para el usuario 117 con password 123
    """

    USERNAME = '115'
    PASSWORD = '123'

    class ErrorMessages:
        ENVIRONMENT = 'No se puede ejecutar este comando en entornos de producción'

    def handle(self, **options):
        if not settings.DEBUG:
            self.stdout.write(self.style.ERROR(Command.ErrorMessages.ENVIRONMENT))
            return

        user = Prestatario.crear_usuario(id=115, username=self.USERNAME, password=self.PASSWORD)

        # materias
        materia1 = Materia.objects.create(
            nombre='Cinematografia',
            periodo='2024-1',
        )

        materia2 = Materia.objects.create(
            nombre='Iluminacion',
            periodo='2024-1',
        )

        # articulos
        articulo1 = Articulo.objects.create(
            nombre="CamaraNikon",
            codigo="123",
        )
        
        articulo2 = Articulo.objects.create(
            nombre="CamaraCanon",
            codigo="111"
        )
        
        unidad1 = Unidad.objects.create(
            estado="ACTIVO",
            articulo=articulo1,
            num_control="1",
            num_serie="1"
        )
        unidad2 = Unidad.objects.create(
            estado="ACTIVO",
            articulo=articulo1,
            num_control="2",
            num_serie="2"
        )
        unidad3 = Unidad.objects.create(
            estado="ACTIVO",
            articulo=articulo1,
            num_control="3",
            num_serie="3"
        )
        unidad4 = Unidad.objects.create(
            estado="ACTIVO",
            articulo=articulo1,
            num_control="4",
            num_serie="4"
        )
        
        unidad5 = Unidad.objects.create(
            estado="ACTIVO",
            articulo=articulo2,
            num_control="5",
            num_serie="5"
        )
        unidad6 = Unidad.objects.create(
            estado="ACTIVO",
            articulo=articulo2,
            num_control="6",
            num_serie="6"
        )
        unidad7 = Unidad.objects.create(
            estado="ACTIVO",
            articulo=articulo2,
            num_control="7",
            num_serie="7"
        )
        unidad8 = Unidad.objects.create(
            estado="ACTIVO",
            articulo=articulo2,
            num_control="8",
            num_serie="8"
        )
        """
        # Unidades
        unidad1 = articulo1.crear_unidad("1", "1")
        unidad2 = articulo1.crear_unidad("2", "2")
        unidad3 = articulo1.crear_unidad("3", "3")
        unidad4 = articulo1.crear_unidad("4", "4")

        unidad5 = articulo2.crear_unidad("5", "5")
        unidad6 = articulo2.crear_unidad("6", "6")
        unidad7 = articulo2.crear_unidad("7", "7")
        unidad8 = articulo2.crear_unidad("8", "8")
        """
        # Agregar articulo a materia
        materia1.agregar_articulo(articulo1)
        materia1.agregar_articulo(articulo2)
        
        # ordenes
        orden1 = Orden.objects.create(
            prestatario=user,
            lugar=Orden.Ubicacion.CAMPUS,
            inicio=make_aware(datetime(2024, 10, 5)),
            final=make_aware(datetime(2024, 10, 5)),
            estado=Orden.Estado.APROBADA,
            materia=materia1,
        )

        orden2 = Orden.objects.create(
            prestatario=user,
            lugar=Orden.Ubicacion.EXTERNO,
            inicio=make_aware(datetime(2024, 10, 5)),
            final=make_aware(datetime(2024, 10, 5)),
            estado=Orden.Estado.APROBADA,
            materia=materia1,
            descripcion="Esta solicitud es para mi practica de Cinematografia en la laguna salada."
        )

        orden3 = Orden.objects.create(
            prestatario=user,
            lugar=Orden.Ubicacion.CAMPUS,
            inicio=make_aware(datetime(2024, 10, 5)),
            final=make_aware(datetime(2024, 10, 5)),
            estado=Orden.Estado.APROBADA,
            materia=materia1,
        )

        orden4 = Orden.objects.create(
            prestatario=user,
            lugar=Orden.Ubicacion.CAMPUS,
            inicio=make_aware(datetime(2024, 10, 5)),
            final=make_aware(datetime(2024, 10, 5)),
            estado=Orden.Estado.APROBADA,
            materia=materia1,
        )

        orden5 = Orden.objects.create(
            prestatario=user,
            lugar=Orden.Ubicacion.CAMPUS,
            inicio=make_aware(datetime(2024, 10, 5)),
            final=make_aware(datetime(2024, 10, 5)),
            estado=Orden.Estado.APROBADA,
            materia=materia1,
        )

        orden6 = Orden.objects.create(
            prestatario=user,
            lugar=Orden.Ubicacion.CAMPUS,
            inicio=make_aware(datetime(2024, 10, 5)),
            final=make_aware(datetime(2024, 10, 5)),
            estado=Orden.Estado.APROBADA,
            materia=materia1,
        )

        #Agregar unidades a las ordenes
        orden1.agregar_unidad(unidad1)
        orden2.agregar_unidad(unidad2)
        orden3.agregar_unidad(unidad3)
        orden4.agregar_unidad(unidad5)
        orden5.agregar_unidad(unidad6)
        orden6.agregar_unidad(unidad7)
        
        
        user.is_superuser = False
        user.is_staff = False

        user.save()
        print('Se guardo usuario...')
        materia1.save()
        materia2.save()
        print('Se guardaron las materias...')
        articulo1.save()
        articulo2.save()
        print('Se guardaron los articulos...')
        unidad1.save()
        unidad2.save()
        unidad3.save()
        unidad4.save()
        unidad5.save()
        unidad6.save()
        unidad7.save()
        unidad8.save()
        print('Se guardaron las unidades...')
        orden1.save()
        orden2.save()
        orden3.save()
        orden4.save()
        orden5.save()
        orden6.save()
        print('Se guardaron las ordenes...')

