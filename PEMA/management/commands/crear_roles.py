from django.core.management.base import BaseCommand
from PEMA.models import Prestatario


class Command(BaseCommand):
    help = 'Crea grupos iniciales'

    def handle(self, *args, **options):
        Prestatario.crear_grupo()
