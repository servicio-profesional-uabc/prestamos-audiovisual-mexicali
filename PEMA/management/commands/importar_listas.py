import re

import pandas as pd
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from PEMA.models import Maestro, Materia, Prestatario


class Command(BaseCommand):
    help = 'Importa datos desde un archivo xls (2003)'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path del archivo xls')

    def handle(self, *args, **options):
        file_path = options['file_path']
        df = pd.read_excel(file_path)
        maestro_data = self.parse_maestro(df)
        materia_data = self.parse_materia(df)
        prestatarios_data = self.parse_prestatarios(file_path)

        self.save_data(maestro_data, materia_data, prestatarios_data)

    def parse_maestro(self, df):
        no_empleado = df.iloc[17, 1]
        nombre_empleado = df.iloc[17, 3]
        return {
            'no_empleado': no_empleado,
            'nombre_empleado': nombre_empleado
        }

    def parse_materia(self, df):
        nombre_materia = df.iloc[13, 3]
        fecha = df.iloc[5, 38]
        anno, semestre = self.parse_fecha(fecha)
        return {
            'nombre_materia': nombre_materia,
            'anno': anno,
            'semestre': semestre
        }

    def parse_fecha(self, fecha):
        partes_fecha = fecha.split("/")
        anno = int(partes_fecha[2])
        semestre = 1 if int(partes_fecha[1]) < 7 else 2
        return anno, semestre

    def parse_prestatarios(self, file_path):
        df = pd.read_excel(file_path, header=21, usecols=['NOMBRE DEL ALUMNO', 'MATRÍCULA'])
        df = df.dropna(subset=['NOMBRE DEL ALUMNO'], how='all')

        patron = r'\d+\s\s'
        final = df[df['NOMBRE DEL ALUMNO'] == 'Fecha/Hora'].index[0]

        nombres = []
        matriculas = []

        for index, row in df.loc[:final - 1].iterrows():
            nombre = re.sub(patron, '', row['NOMBRE DEL ALUMNO'])
            matricula = int(row['MATRÍCULA'])
            nombres.append(nombre)
            matriculas.append(matricula)

        return list(zip(nombres, matriculas))

    def save_data(self, maestro_data, materia_data, prestatarios_data):
        materia = self.get_or_create_materia(materia_data)
        maestro = self.get_or_create_maestro(maestro_data)

        if maestro:
            materia.agregar_maestro(maestro)

        for nombre, matricula in prestatarios_data:
            prestatario = self.get_or_create_prestatario(nombre, matricula)
            if prestatario:
                materia.agregar_alumno(prestatario)

    def get_or_create_materia(self, materia_data):
        return Materia.objects.get_or_create(
            nombre=materia_data['nombre_materia'],
            year=materia_data['anno'],
            semestre=materia_data['semestre']
        )[0]

    def get_or_create_maestro(self, maestro_data):

        numero_empleado = maestro_data['no_empleado']

        if User.objects.filter(username=numero_empleado).exists():
            self.stdout.write(
                self.style.ERROR(f"Error: El maestro con número de empleado {numero_empleado} ya existe."))
            return None

        return Maestro.crear_usuario(
            username=numero_empleado,
            first_name=maestro_data['nombre_empleado'],
            password=str(numero_empleado)
        )

    def get_or_create_prestatario(self, nombre, matricula):

        if User.objects.filter(username=matricula).exists():
            self.stdout.write(self.style.ERROR(f"Error: El prestatario con matrícula {matricula} ya existe."))
            return None

        return Prestatario.crear_usuario(
            username=matricula,
            first_name=nombre,
            password=str(matricula)
        )
