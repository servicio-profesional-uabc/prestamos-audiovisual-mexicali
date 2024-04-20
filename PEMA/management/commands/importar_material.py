import pandas as pd
from openpyxl import load_workbook
from django.core.management.base import BaseCommand
from PEMA.models import Articulo


class Command(BaseCommand):
    help = 'Importa datos desde un archivo Excel.'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Ruta del archivo Excel.')

    def handle(self, *args, **options):
        file_path = options['file_path']
        self.importar_material(file_path)

    def importar_material(self, file_path):
        """
        Importa los datos de la lista de material.
        :param file_path:
        :return:
        """
        wb = load_workbook(file_path)
        sheet = wb.active

        # encontrar el indice de la ultima fila con datos en la columna de nombres (refactorizar esto)
        ultima_fila = sheet.max_row
        for fila in range(sheet.max_row, 1, -1):
            # verificar si la celda en la columna no esta vacia
            if sheet.cell(row=fila, column=3).value is not None:
                ultima_fila = fila
                break

        # leer SOLO las filas necesarias hasta la ultima fila con datos
        df = pd.read_excel(file_path, nrows=ultima_fila)

        for index, row in df.iterrows():
            # obtener los datos relevantes
            num_control = row['NÚMERO DE CONTROL']
            num_serie = row['NÚMERO DE SERIE']
            nombre_articulo = row['NOMBRE Y MODELO DEL EQUIPO']

            articulo, creado = Articulo.objects.get_or_create(
                nombre=nombre_articulo
            )

            # crear unidad
            unidad, creada = articulo.crear_unidad(num_control=num_control, num_serie=num_serie)
