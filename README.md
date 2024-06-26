[![Django CI](https://github.com/servicio-profesional-uabc/prestamos-audiovisual-mexicali/actions/workflows/django.yml/badge.svg)](https://github.com/servicio-profesional-uabc/prestamos-audiovisual-mexicali/actions/workflows/django.yml)

## Sistema de Gestión de Préstamos
PEMA simplifica la gestión de préstamos de material audiovisual en la Facultad de Artes del campus Mexicali. 
Desarrollado en Python y Django.

### Documentación
La documentación se genera con Sphinx. 
Ejecuta este comando para generarla: `sphinx-build ./docs ./docs/_build/html`. la documentacion se generara en 
`./docs/_build/html` 

### Pruebas
Se usan herramientas de Django para pruebas unitarias. **Mantén las pruebas actualizadas para asegurar la calidad del 
código**:

- Pruebas unitarias: 
  - `python manage.py test PEMA/tests`
  
Cobertura de código: 
```shell
coverage run manage.py test PEMA
coverage report
```

### Modo Porducción
- Preparar el entorno
```shell
python manage.py makemigrations PEMA --settings=prestamos.settings.prod
python manage.py migrate --settings=prestamos.settings.prod
python manage.py crear_roles --settings=prestamos.settings.prod
python manage.py loaddata tema_cepa.json --settings=prestamos.settings.prod
```
  
- Ejecutar el servidor
  - `python manage.py runserver --settings=prestamos.settings.prod`

### Setup para Desarolladores
- Crear entorno virtual: 
  - `python -m venv .venv`
- Activar el entorno virtual:
  - `.venv\Scripts\activate`
- Instalar dependencias: 
  - `pip install -r requirements.txt`
- Generar modelos y usuarios de prueba: 
  - `python manage.py makemigrations PEMA`
  - `python manage.py migrate` 
  - `python manage.py developer_setup`

### Datos de Prueba
- Artículos y unidades de prueba: 
  - `python manage.py importar_material data/inventario.xlsx`
- Personal (Maestros) de prueba: 
  - `python manage.py importar_personal data/personal.xlsx`
- Materia (lista de asistencia) de prueba: 
  - `python manage.py importar_listas data/lista.xls`

### Cargar tema de admin
- Comando para cargar tema de admin: 
  - `python manage.py loaddata tema_cepa.json`
- Comando para guardar tema de admin: 
  - `python manage.py dumpdata admin_interface.Theme --pks=1 > tema_cepa.json`
