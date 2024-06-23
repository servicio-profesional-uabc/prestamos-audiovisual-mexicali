from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from PEMA.models import Prestatario, Orden, Materia, Articulo, Unidad, Categoria, Ubicacion
from django.utils.timezone import make_aware
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
        materia1, created = Materia.objects.get_or_create(
            nombre='Cinematografia',
            year = 2024,
            semestre = 1
        )
        materia2, created = Materia.objects.get_or_create(
            nombre='Iluminacion',
            year = 2024,
            semestre = 1
        )

        materia1.agregar_alumno(user)
        materia2.agregar_alumno(user)
        
        # Categorias
        categoria1, created = Categoria.objects.get_or_create(
            nombre="Camaras"
        )
        categoria2, created = Categoria.objects.get_or_create(
            nombre="Iluminación"
        )
        
        # articulos
        articulo1, created = Articulo.objects.get_or_create(
            nombre="CamaraNikon",
            codigo="123",
        )
        
        articulo2, created = Articulo.objects.get_or_create(
            nombre="CamaraCanon",
            codigo="111"
        )
        
        categoria1.agregar(articulo=articulo1)
        categoria1.agregar(articulo=articulo2)
        
        """        
        unidad1, created = Unidad.objects.get_or_create(
            estado=Unidad.Estado.ACTIVO,
            articulo=articulo1,
            num_control="1",
            num_serie="1"
        )
        unidad2, created = Unidad.objects.get_or_create(
            estado=Unidad.Estado.ACTIVO,
            articulo=articulo2,
            num_control="2",
            num_serie="2"
        )
        unidad3, created = Unidad.objects.get_or_create(
            estado=Unidad.Estado.ACTIVO,
            articulo=articulo1,
            num_control="3",
            num_serie="3"
        )
        unidad4, created = Unidad.objects.get_or_create(
            estado=Unidad.Estado.ACTIVO,
            articulo=articulo1,
            num_control="4",
            num_serie="4"
        )
        
        unidad5, created = Unidad.objects.get_or_create(
            estado=Unidad.Estado.ACTIVO,
            articulo=articulo2,
            num_control="5",
            num_serie="5"
        )
        unidad6, created = Unidad.objects.get_or_create(
            estado=Unidad.Estado.ACTIVO,
            articulo=articulo2,
            num_control="6",
            num_serie="6"
        )
        unidad7, created = Unidad.objects.get_or_create(
            estado=Unidad.Estado.ACTIVO,
            articulo=articulo2,
            num_control="7",
            num_serie="7"
        )
        unidad8, created = Unidad.objects.get_or_create(
            estado=Unidad.Estado.ACTIVO,
            articulo=articulo2,
            num_control="8",
            num_serie="8"
        ) 
        """
        
        unidad1, created = articulo1.crear_unidad(num_control="1", num_serie="1")
        unidad2, created = articulo2.crear_unidad(num_control="2", num_serie="2")
        unidad3, created = articulo1.crear_unidad(num_control="3", num_serie="3")
        unidad4, created = articulo1.crear_unidad(num_control="4", num_serie="4")
        unidad5, created = articulo2.crear_unidad(num_control="5", num_serie="5")
        unidad6, created = articulo2.crear_unidad(num_control="6", num_serie="6")
        unidad7, created = articulo2.crear_unidad(num_control="7", num_serie="7")
        unidad8, created = articulo2.crear_unidad(num_control="8", num_serie="8")
        unidad1.estado = Unidad.Estado.ACTIVO
        unidad2.estado = Unidad.Estado.ACTIVO
        unidad3.estado = Unidad.Estado.ACTIVO
        unidad4.estado = Unidad.Estado.ACTIVO
        unidad5.estado = Unidad.Estado.ACTIVO
        unidad6.estado = Unidad.Estado.ACTIVO
        unidad7.estado = Unidad.Estado.ACTIVO
        unidad8.estado = Unidad.Estado.ACTIVO 

        
        # Agregar articulo a materia
        materia1.agregar_articulo(articulo1)
        materia1.agregar_articulo(articulo2)

        # ordenes
        orden1, created = Orden.objects.get_or_create(
            nombre="Awa1",
            prestatario=user,
            lugar=Ubicacion.CAMPUS,
            inicio=make_aware(datetime(2024, 10, 5, 12)),
            final=make_aware(datetime(2024, 10, 5, 14)),
            estado='RS',
            materia=materia1,
        )

        orden2, created = Orden.objects.get_or_create(            
            nombre="Awa2",
            prestatario=user,
            lugar=Ubicacion.CAMPUS,
            inicio=make_aware(datetime(2024, 10, 5, 11)),
            final=make_aware(datetime(2024, 10, 5, 14)),
            estado='RS',
            materia=materia1,
            descripcion="Esta solicitud es para mi practica de Cinematografia en la laguna salada."
        )

        orden3, created = Orden.objects.get_or_create(
            nombre="Awa3",
            prestatario=user,
            lugar=Ubicacion.CAMPUS,
            inicio=make_aware(datetime(2024, 10, 5, 15)),
            final=make_aware(datetime(2024, 10, 5, 17)),
            estado='RS',
            materia=materia1,
        )

        orden4, created = Orden.objects.get_or_create(
            nombre="Awa4",
            prestatario=user,
            lugar=Ubicacion.CAMPUS,
            inicio=make_aware(datetime(2024, 10, 5, 16)),
            final=make_aware(datetime(2024, 10, 5, 18)),
            estado='RS',
            materia=materia1,
        )

        orden5, created = Orden.objects.get_or_create(
            nombre="Awa5",
            prestatario=user,
            lugar=Ubicacion.CAMPUS,
            inicio=make_aware(datetime(2024, 10, 5, 13)),
            final=make_aware(datetime(2024, 10, 5, 16)),
            estado="AP",
            materia=materia1,
        )

        orden6, created = Orden.objects.get_or_create(
            nombre="Awa6",
            prestatario=user,
            lugar=Ubicacion.CAMPUS,
            inicio=make_aware(datetime(2024, 10, 5, 11)),
            final=make_aware(datetime(2024, 10, 5, 18)),
            estado="AP",
            materia=materia1,
        )

        # Agregar unidades a las ordenes
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
        categoria1.save()
        categoria2.save()
        print('Se guardaron las categorias...')
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

        print('orden1:')
        print(orden1.inicio)
        print(orden1.final)
        print('orden2:')
        print(orden2.inicio)
        print(orden2.final)
        print('orden3:')
        print(orden3.inicio)
        print(orden3.final)
        print('orden4:')
        print(orden4.inicio)
        print(orden4.final)
        print('orden5:')
        print(orden5.inicio)
        print(orden5.final)
        print('orden6:')
        print(orden6.inicio)
        print(orden6.final)
        print("articulo1")
        print("Disponible:", articulo1.disponible(make_aware(datetime(2024, 10, 5, 12)), make_aware(datetime(2024, 10, 5, 14))))

        print("articulo1")
        print("Disponible:", articulo1.disponible(make_aware(datetime(2024, 10, 5, 11)), make_aware(datetime(2024, 10, 5, 14))))

        print("articulo2")
        print("Disponible:", articulo2.disponible(make_aware(datetime(2024, 10, 5, 14)), make_aware(datetime(2024, 10, 5, 16))))
        
        print(materia1.alumnos())
        
        print(Prestatario.materias(user))
        
        unidades = Unidad.objects.all()
        print(Unidad.Estado.ACTIVO)
        for u in unidades:
            print(u.articulo)
            print(u.estado)