import pandas as pd
from django.core.management.base import BaseCommand
from PEMA.models import Articulo, Unidad

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
        # Leer todas las filas del archivo Excel usando pandas
        df = pd.read_excel(file_path)

        # Encontrar el índice de la última fila con datos en la columna 'NOMBRE Y MODELO DEL EQUIPO'
        ultima_fila = df[df['NOMBRE Y MODELO DEL EQUIPO'].notna()].index[-1] + 1

        # Leer solo hasta la última fila con datos
        df = pd.read_excel(file_path, nrows=ultima_fila)

        for index, row in df.iterrows():
            # Obtener los datos relevantes
            num_control = row['NÚMERO DE CONTROL']
            num_serie = row['NÚMERO DE SERIE']
            nombre_articulo = row['NOMBRE Y MODELO DEL EQUIPO']

            # Buscar el artículo existente por nombre
            articulo, creado = Articulo.objects.get_or_create(nombre=nombre_articulo)

            # Verificar si la unidad ya existe para el artículo y num_control
            try:
                unidad = Unidad.objects.get(articulo=articulo, num_control=num_control, num_serie=num_serie)
            except Unidad.DoesNotExist:
                # Crear unidad solo si no existe
                if num_serie:
                    # Buscar una unidad existente que tenga el num_serie
                    try:
                        unidad = Unidad.objects.get(articulo=articulo, num_serie=num_serie, num_control=num_control)
                    except Unidad.DoesNotExist:
                        # Crear una nueva unidad solo si no existe con el mismo num_serie
                        unidad = Unidad.objects.create(articulo=articulo, num_control=num_control, num_serie=num_serie)
                else:
                    # Si no hay num_serie, usar solo num_control para la unicidad
                    unidad, creada = articulo.crear_unidad(num_control=num_control, num_serie=num_serie)
