from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from PEMA.models import Prestatario, Orden, Materia, EstadoOrden, TipoOrden, UsuarioMateria
from django.utils.timezone import make_aware
from datetime import datetime
from django.conf import settings


class Command(BaseCommand):
    """
    *NO usar en producción*
    Crea materias y usuario para el usuario 117 con password 123
    """

    USERNAME = '117'
    PASSWORD = '123'
    ID = 117

    class ErrorMessages:
        ENVIRONMENT = 'No se puede ejecutar este comando en entornos de producción'

    def handle(self, **options):
        if not settings.DEBUG:
            self.stdout.write(self.style.ERROR(Command.ErrorMessages.ENVIRONMENT))
            return

        try:
            user = Prestatario.crear_usuario(id=self.ID, username=self.USERNAME, password=self.PASSWORD)
            print("Se guardo el usuario...")
        except:
            user = User.objects.get(id=self.ID)
            print("El usuario ya existe, continuando con lo siguiente...")
        finally:
            user.is_superuser = False
            user.is_staff = False
            user.save()

        # materias
        materia1, created = Materia.objects.get_or_create(
            nombre='Cinematografia',
            year=2024,
            semestre=1,
            activa=True,
        )
        materia1.save()
        print(f'La materia {materia1.nombre} se ha guardado...')


        materia2, created = Materia.objects.get_or_create(
            nombre='Iluminacion',
            year=2024,
            semestre=1,
            activa=True,
        )
        materia2.save()
        print(f'La materia {materia2.nombre} se ha guardado...')

        usuariomateria, created = UsuarioMateria.objects.get_or_create(
            usuario=User.objects.get(id=self.ID),
            materia=materia1,
        )
        usuariomateria.save()
        print(f'La {materia1} y usuario se han relacionado...')

        usuariomateria, created = UsuarioMateria.objects.get_or_create(
            usuario=User.objects.get(id=self.ID),
            materia=materia2,
        )
        usuariomateria.save()
        print(f'La {materia2} y usuario se han relacionado...')

