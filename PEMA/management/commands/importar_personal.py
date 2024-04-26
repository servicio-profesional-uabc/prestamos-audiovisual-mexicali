import pandas as pd
from django.core.management.base import BaseCommand
from PEMA.models import Maestro


class Command(BaseCommand):
    help = 'Importa datos desde un archivo xlsx'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path del archivo xlsx')

    def handle(self, *args, **options):
        file_path = options['file_path']
        self.importar_personal(file_path)

    def importar_personal(self, file_path):
        """
        Importa la lista de personal del CEPA
        :param file_path: Path del archivo xlsx con la lista de personal
        :return:
        """
        df = pd.read_excel(file_path, header=1)

        for index, row in df.iterrows():
            username = row['NUMERO DE EMPLEADO']
            firstname = row['PERSONAL DEL CEPA']

            maestro = Maestro.crear_usuario(username=username, first_name=firstname, password=str(username))
