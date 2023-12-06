from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User


class Command(BaseCommand):
    """
    Crea un superusuario de prueba
    """

    SUPERUSER_NAME = 'admin'
    SUPERUSER_PASSWORD = '123'

    def handle(self, **options):
        # https://stackoverflow.com/a/18504852/22015904
        user = User.objects.create_user(
            username=Command.SUPERUSER_NAME,
            password=Command.SUPERUSER_PASSWORD,
        )

        user.is_superuser = True
        user.is_staff = True

        user.save()
