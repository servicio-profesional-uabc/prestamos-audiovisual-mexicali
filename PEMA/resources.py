import pandas as pd
import tablib
from django.contrib.auth.models import User
from import_export.fields import Field
from import_export.widgets import ForeignKeyWidget
from import_export import resources
from PEMA.models import Maestro, Articulo, Unidad, Prestatario


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
        data.headers = ['NOMBRE_DEL_ALUMNO', 'MATRICULA']
        for i in subseccion:
            data.append([i[1], str(i[8])])

        cleaned_data = data
        return super().import_data(cleaned_data, **kwargs)

    def after_save_instance(self, instance, row, **kwargs):
        print(instance)
        grupo, _ = Prestatario.crear_grupo()
        grupo.user_set.add(instance)


class MaestroResource(resources.ModelResource):
    username = Field(attribute='username', column_name='NUMERO DE EMPLEADO')
    first_name = Field(attribute='first_name', column_name='PERSONAL DEL CEPA')

    class Meta:
        model = Maestro
        skip_unchanged = True
        report_skipped = False
        #start_row = 3  # Empezar a leer desde la tercera fila
        header_row = 2  # Utilizar la segunda fila como encabezados de columna
        import_id_fields = ('username',)
        fields = ('username', 'first_name')


class ArticuloResource(resources.ModelResource):
    nombre = Field(attribute='nombre', column_name='NOMBRE Y MODELO DEL EQUIPO')

    class Meta:
        model = Articulo
        import_id_fields = ('nombre',)
        fields = ('nombre',)


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

    def before_import_row(self, row, **kwargs):
        nombre_articulo = row['NOMBRE Y MODELO DEL EQUIPO']
        articulo, created = Articulo.objects.get_or_create(nombre=nombre_articulo)
        row['articulo'] = articulo.id

    def skip_row(self, instance, original, row, import_validation_errors=None):
        # Evitar la creación de duplicados
        if Unidad.objects.filter(articulo=instance.articulo, num_control=instance.num_control,
                                 num_serie=instance.num_serie).exists():
            return True
        return super().skip_row(instance, original, row, import_validation_errors)
