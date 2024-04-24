from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware


from PEMA.models import Prestatario, Orden, Materia, Articulo


class Command(BaseCommand):
    """
    *NO usar en producción*
    Crea ordenes de diferentes estados y usuario para el usuario 117 con password 123
    """

    USERNAME = 'P. Crear Unidades'
    PASSWORD = '123'
    ID = '115'

    class ErrorMessages:
        ENVIRONMENT = 'No se puede ejecutar este comando en entornos de producción'

    def handle(self, **options):
        if not settings.DEBUG:
            self.stdout.write(self.style.ERROR(Command.ErrorMessages.ENVIRONMENT))
            return

        user = Prestatario.crear_usuario(id=self.ID, username=self.USERNAME, password=self.PASSWORD)

        # materias
        materia1, _ = Materia.objects.get_or_create(nombre='Cinematografia', year=2024, semestre=1)
        materia2, _ = Materia.objects.get_or_create(nombre='Iluminacion', year=2024, semestre=1)

        # articulos
        articulo1 = Articulo.objects.create(nombre="Camara Nikon", codigo="123", )
        articulo2 = Articulo.objects.create(nombre="Camara Canon", codigo="111")

        # unidades
        unidad1, _ = articulo1.crear_unidad(num_control="1", num_serie="1")
        unidad2, _ = articulo2.crear_unidad(num_control="2", num_serie="2")
        unidad3, _ = articulo1.crear_unidad(num_control="3", num_serie="3")
        unidad4, _ = articulo1.crear_unidad(num_control="4", num_serie="4")
        unidad5, _ = articulo2.crear_unidad(num_control="5", num_serie="5")
        unidad6, _ = articulo2.crear_unidad(num_control="6", num_serie="6")
        unidad7, _ = articulo2.crear_unidad(num_control="7", num_serie="7")
        unidad8, _ = articulo2.crear_unidad(num_control="8", num_serie="8")

        # Agregar articulo a materia
        materia1.agregar_articulo(articulo1)
        materia1.agregar_articulo(articulo2)

        # ordenes
        orden1, _ = Orden.objects.get_or_create(prestatario=user,lugar=Orden.Ubicacion.CAMPUS, inicio=make_aware(datetime(2024, 10, 5)),
            final=make_aware(datetime(2024, 10, 5)), estado="AP", materia=materia1, )

        orden1.agregar_corresponsable(user)

        orden2, _ = Orden.objects.get_or_create(prestatario=user,lugar=Orden.Ubicacion.EXTERNO, inicio=make_aware(datetime(2024, 10, 5)),
            final=make_aware(datetime(2024, 10, 5)), estado="AP", materia=materia1,
            descripcion="Esta solicitud es para mi practica de Cinematografia en la laguna salada.")

        orden2.agregar_corresponsable(user)

        orden3, _ = Orden.objects.get_or_create(prestatario=user, lugar=Orden.Ubicacion.CAMPUS, inicio=make_aware(datetime(2024, 10, 5)),
            final=make_aware(datetime(2024, 10, 5)), estado="AP", materia=materia1, )

        orden3.agregar_corresponsable(user)

        orden4, _ = Orden.objects.get_or_create(prestatario=user, lugar=Orden.Ubicacion.CAMPUS, inicio=make_aware(datetime(2024, 10, 5)),
            final=make_aware(datetime(2024, 10, 5)), estado="AP", materia=materia1, )

        orden4.agregar_corresponsable(user)

        orden5, _ = Orden.objects.get_or_create(prestatario=user, lugar=Orden.Ubicacion.CAMPUS, inicio=make_aware(datetime(2024, 10, 5)),
            final=make_aware(datetime(2024, 10, 5)), estado="AP", materia=materia1, )

        orden5.agregar_corresponsable(user)

        orden6, _ = Orden.objects.get_or_create(prestatario=user, lugar=Orden.Ubicacion.CAMPUS, inicio=make_aware(datetime(2024, 10, 5)),
            final=make_aware(datetime(2024, 10, 5)), estado="AP", materia=materia1, )

        orden6.agregar_corresponsable(user)

        # Agregar unidades a las ordenes
        orden1.agregar_unidad(unidad1)
        orden2.agregar_unidad(unidad2)
        orden3.agregar_unidad(unidad3)
        orden4.agregar_unidad(unidad5)
        orden5.agregar_unidad(unidad6)
        orden6.agregar_unidad(unidad7)
