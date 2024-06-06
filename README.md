[![Django CI](https://github.com/servicio-profesional-uabc/prestamos-audiovisual-mexicali/actions/workflows/django.yml/badge.svg)](https://github.com/servicio-profesional-uabc/prestamos-audiovisual-mexicali/actions/workflows/django.yml)

## Sistema de Gestión de Préstamos de Material Audiovisual (PEMA)
PEMA simplifica la gestión de préstamos de material audiovisual en la Facultad de Artes del campus Mexicali. 
Desarrollado en Python y Django.

### Documentación
La documentación se genera con Sphinx. 
Ejecuta este comando para generarla: `sphinx-build ./docs ./docs/_build/html`. la documentacion se generara en 
`./docs/_build/html` 

### Pruebas
Se usan herramientas de Django para pruebas unitarias. Mantén las pruebas actualizadas para asegurar la calidad del 
código:

- Pruebas unitarias: `python manage.py test PEMA/tests`
- Cobertura de código: `coverage run manage.py test PEMA` y `coverage report`

### Setup rapido
- Crear entorno virtual: `python -m venv .venv` y `.venv\Scripts\activate`
- Instalar dependencias: `pip install -r requirements.txt`
- Generar modelos y usuarios de prueba: `python manage.py makemigrations PEMA`, `python manage.py migrate` y 
`python manage.py developer_setup`

### Datos de Prueba
- Artículos y unidades de prueba: `python manage.py importar_material data/inventario.xlsx`
- Personal (Maestros) de prueba: `python manage.py importar_personal data/personal.xlsx`
- Materia (lista de asistencia) de prueba: `python manage.py importar_listas data/lista.xls`
