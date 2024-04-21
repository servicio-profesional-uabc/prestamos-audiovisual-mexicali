import pandas as pd
from openpyxl import load_workbook
from PEMA.models import Articulo
from PEMA.models import Maestro


def importar_material(file_path):
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

def importar_personal(file_path):
    """
    Importa la lista de personal del CEPA
    :param file_path: [ath del archivo xlsx
    :return:
    """
    df = pd.read_excel(file_path, header=1)

    for index, row in df.iterrows():
        username = row['NUMERO DE EMPLEADO']
        first_name = row['PERSONAL DEL CEPA']

    maestro, creado = Maestro.crear_usuario(
        username=username,
        first_name=first_name
    )

'''
# pathInventario = r"C:\Users\Hecta\Documents\test pandas\Inventario CEPA (Actualizado nov 2023).xlsx"
file = 'Lista de personal del CEPA (docentes quienes piden).xlsx'

dataPersonal = pd.read_excel(file)

for index, row in dataPersonal.iterrows():
    # obtener datos de la fila
    nombre = row['PERSONAL DEL CEPA']
    matricula = row['NUMERO DE EMPLEADO']

    # crear usuario prestatario
    user = Prestatario.crear_usuario(username=matricula, password=matricula)

    """
    # asignar usuario al grupo 'prestatarios'
    group, _ = Prestatario.crear_grupo()
    group.user_set.add(user)

    # otorgar permisos al usuario prestatario
    # esto es un ejemplo (revisar como se hace el mappeo):
    permisos = Permission.objects.filter(codename__in=['add_carrito', 'add_orden', 'add_corresponsableorden'])
    user.user_permissions.add(*permisos)
    """
'''
