import pandas as pd
from PEMA.models import Prestatario

# pathInventario = r"C:\Users\Hecta\Documents\test pandas\Inventario CEPA (Actualizado nov 2023).xlsx"
file = 'Lista de personal del CEPA (docentes quienes piden).xlsx'

dataPersonal = pd.read_excel(file)

for index, row in dataPersonal.iterrows():
    # obtener datos de la fila
    nombre = row['PERSONAL DEL CEPA']
    matricula = row['NUMERO DE EMPLEADO']

    # crear usuario prestatario
    user = Prestatario.crear_usuario(username=matricula, password='')

    # asignar usuario al grupo 'prestatarios'
    group, _ = Prestatario.crear_grupo()
    group.user_set.add(user)

    # otorgar permisos al usuario prestatario
    # esto es un ejemplo (revisar como se hace el mappeo):
    permisos = Permission.objects.filter(codename__in=['add_carrito', 'add_orden', 'add_corresponsableorden'])
    user.user_permissions.add(*permisos)
