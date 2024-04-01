import pandas as pd
from PEMA.models import Prestatario

# pathInventario = r"C:\Users\Hecta\Documents\test pandas\Inventario CEPA (Actualizado nov 2023).xlsx"
file = 'Lista de personal del CEPA (docentes quienes piden).xlsx'

dataPersonal = pd.read_excel(file)


for index, row in dataPersonal.iterrows():
    # Obtener datos de la fila
    nombre = row['PERSONAL DEL CEPA']
    matricula = row['NUMERO DE EMPLEADO']

    # Crear usuario prestatario
    user = Prestatario.crear_usuario(username=matricula, password='contraseña_por_defecto')

    # Asignar usuario al grupo 'prestatarios'
    group, _ = Prestatario.crear_grupo()
    group.user_set.add(user)

    # Otorgar permisos al usuario prestatario
    # Esto es un ejemplo, asegúrate de otorgar los permisos correctos según tus requisitos
    permisos = Permission.objects.filter(codename__in=['add_carrito', 'add_orden', 'add_corresponsableorden'])
    user.user_permissions.add(*permisos)

    # Guardar cambios en la base de datos
    user.save()
