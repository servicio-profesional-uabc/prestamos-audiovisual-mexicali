import pandas as pd
import tablib
import re
from django.contrib.auth.models import User
from import_export.fields import Field
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from import_export import resources
from PEMA.models import Maestro, Articulo, Unidad, Prestatario, Materia


class MateriaResource(resources.ModelResource):
    nombre = Field(attribute='nombre', column_name='NOMBRE_DE_LA_MATERIA')
    year = Field(attribute='year', column_name='AÑO')
    semestre = Field(attribute='semestre', column_name='SEMESTRE')

    maestro = Field(
        attribute='maestro',
        column_name='MAESTRO',
        widget=ManyToManyWidget(Maestro),
    )

    class Meta:
        model = Materia
        skip_unchanged = True
        report_skipped = False
        import_id_fields = ('nombre',)
        fields = ('NOMBRE_DE_LA_MATERIA', 'AÑO', 'SEMESTRE')

    def import_data(self, dataset, **kwargs):

        data = tablib.Dataset()
        data.headers = ['NOMBRE_DE_LA_MATERIA', 'AÑO', 'SEMESTRE']


class PrestatarioResource(resources.ModelResource):
    # Define los campos y los nombres de los headers personalizados
    username = Field(attribute='username', column_name='MATRICULA')
    first_name = Field(attribute='first_name', column_name='NOMBRE_DEL_ALUMNO')

    class Meta:
        model = User
        skip_unchanged = True
        report_skipped = False
        import_id_fields = ('username',)
        fields = ('NOMBRE_DEL_ALUMNO', 'MATRICULA')

    def import_data(self, dataset, **kwargs):
        """
        Limpiar los datos de la lista, solo se extraen a los usuarios
        """
        subseccion = dataset[23:len(dataset) - 4]

        data = tablib.Dataset()

        # Expresion regular para quitar enumeraciones de alumnos
        patron = r'\d+\s\s'

        # Expresion regular para quitar decimales de matriculas
        patron_decimal = r'\.\d+'

        # Aqui se acomodan los datos para alumnos (prestatarios)
        data.headers = ['NOMBRE_DEL_ALUMNO', 'MATRICULA']
        for i in subseccion:
            nombre = nombre = re.sub(patron, '', i[1])
            matricula = re.sub(patron_decimal, '', str(i[8]))
            data.append([nombre, matricula])

        cleaned_data = data
        return super().import_data(cleaned_data, **kwargs)

    def after_save_instance(self, instance, row, **kwargs):
        print(instance)
        grupo, _ = Prestatario.crear_grupo()
        grupo.user_set.add(instance)


class EmpleadoResource(resources.ModelResource):
    username = Field(attribute='username', column_name='NUMERO DE EMPLEADO')
    first_name = Field(attribute='first_name', column_name='PERSONAL DEL CEPA')

    class Meta:
        model = Maestro
        skip_unchanged = True
        report_skipped = False
        import_id_fields = ('username',)
        fields = ('username', 'first_name')

    def import_data(self, dataset, **kwargs):
        """
        Limpiar los datos, solo se extraen filas que no tengan valor
        nulo en su 'NOMBRE Y MODELO DEL EQUIPO'
        """

        data = tablib.Dataset()
        data.headers = ['PERSONAL DEL CEPA', 'NUMERO DE EMPLEADO']

        # Rellenar el nuevo dataset con los datos a partir de la row 1 del...
        # ...dataset original
        for i in range(1, len(dataset)):
            fila = dataset[i]
            datos_filtrados = [fila[0], fila[1]]
            data.append(datos_filtrados)

        return super().import_data(data, **kwargs)


class UnidadResource(resources.ModelResource):
    num_control = Field(attribute='num_control', column_name='NÚMERO DE CONTROL')
    num_serie = Field(attribute='num_serie', column_name='NÚMERO DE SERIE')

    articulo = Field(
        column_name='NOMBRE Y MODELO DEL EQUIPO',
        attribute='articulo',
        widget=ForeignKeyWidget(Articulo, 'nombre')
    )

    class Meta:
        model = Unidad
        import_id_fields = ('num_control', 'num_serie', 'articulo')
        fields = ('articulo', 'num_control', 'num_serie')

    def import_data(self, dataset, **kwargs):
        """
        Limpiar los datos, solo se extraen filas que no tengan valor
        nulo en su 'NOMBRE Y MODELO DEL EQUIPO'
        """

        data = tablib.Dataset(headers=dataset.headers[:3])

        for i in dataset:
            if i[2] is None:
                break
            data.append(i[:3])

        print(data)

        return super().import_data(data, **kwargs)

    def before_import_row(self, row, **kwargs):
        nombre_articulo = row['NOMBRE Y MODELO DEL EQUIPO']
        articulo, created = Articulo.objects.get_or_create(nombre=nombre_articulo)
        row['articulo'] = articulo.id

        # Manejar valores nulos
        if not row['NÚMERO DE SERIE']:
            row['NÚMERO DE SERIE'] = ''
        if not row['NÚMERO DE CONTROL']:
            row['NÚMERO DE CONTROL'] = ''

    def skip_row(self, instance, original, row, import_validation_errors=None):
        # Evitar la creación de duplicados
        if Unidad.objects.filter(articulo=instance.articulo, num_control=instance.num_control,
                                 num_serie=instance.num_serie).exists():
            return True
        return super().skip_row(instance, original, row, import_validation_errors)
