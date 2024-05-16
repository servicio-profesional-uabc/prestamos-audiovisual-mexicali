import pandas as pd
import re
from django.core.management.base import BaseCommand
from PEMA.models import Maestro
from PEMA.models import Materia
from PEMA.models import Prestatario


class Command(BaseCommand):
    help = 'Importa datos desde un archivo xls (2003)'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path del archivo xls')

    def handle(self, *args, **options):
        file_path = options['file_path']
        self.importar_listas(file_path)

    def importar_listas(self, file_path):
        # Cargar el archivo una vez
        df = pd.read_excel(file_path)

        """Parsear maestro"""
        # Obtener el num de empleado y nombre
        no_empleado = df.iloc[17, 1]
        nombre_empleado = df.iloc[17, 3]

        """Parsear materia"""
        # Obtener el nombre de la materia y la fecha
        nombre_materia = df.iloc[13, 3]
        fecha = df.iloc[5, 38]

        # dividir la fecha utilizando "/"
        partes_fecha = fecha.split("/")
        # obtener el anno (la tercera parte)
        anno = int(partes_fecha[2])
        if int(partes_fecha[1]) < 7:
            semestre = 1
        else:
            semestre = 2

        """Parsear prestatarios"""
        # Para evitar que pandas detecte 'unnamed n' columnas, releemos el
        # archivo para usar usecols en read_excel().
        df = pd.read_excel(file_path, header=21, usecols=['NOMBRE DEL ALUMNO', 'MATRÍCULA'])

        # Eliminar filas vacias o NAN
        df = df.dropna(subset=['NOMBRE DEL ALUMNO'], how='all')

        # Definir patron de expresion regular para encontrar numeros seguidos de dos espacios
        patron = r'\d+\s\s'

        # Encontrar el índice de la primera fila que contiene "Fecha/Hora"
        final = df[df['NOMBRE DEL ALUMNO'] == 'Fecha/Hora'].index[0]

        nombres = []
        matriculas = []

        # Iterar sobre los datos completos
        for index, row in df.loc[:final - 1].iterrows():
            nombre = row['NOMBRE DEL ALUMNO']
            matricula = row['MATRÍCULA']

            # Reemplazar el patron definido por una cadena vacia
            nombre = re.sub(patron, '', nombre)
            nombres.append(nombre)
            matriculas.append(int(matricula))

        self.parsear_listas(nombre_materia, anno, semestre, no_empleado, nombre_empleado, nombres, matriculas)

    def parsear_listas(self, nombre_materia, anno, semestre, no_empleado, nombre_empleado, nombres, matriculas):
        """Crear Materia"""
        materia = Materia.objects.get_or_create(nombre=nombre_materia, year=anno, semestre=semestre)[0]

        """Crear maestro"""
        maestro = Maestro.crear_usuario(username=no_empleado, first_name=nombre_empleado, password=str(no_empleado))
        # agregar maestro a la materia
        materia.agregar_maestro(maestro)

        """Crear Prestatarios"""
        for nombre, matricula in zip(nombres, matriculas):
            prestatario = Prestatario.crear_usuario(username=matricula, first_name=nombre,
                                                    password=str(matricula))
            # agregar prestatario a materia
            materia.agregar_alumno(prestatario)
