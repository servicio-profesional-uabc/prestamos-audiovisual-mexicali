[![Django CI](https://github.com/servicio-profesional-uabc/prestamos-audiovisual-mexicali/actions/workflows/django.yml/badge.svg)](https://github.com/servicio-profesional-uabc/prestamos-audiovisual-mexicali/actions/workflows/django.yml)

# Sistema de Gestión de Préstamos de Material Audiovisual (PEMA)
PEMA es una herramienta diseñada para simplificar la gestión de préstamos de material de grabación audiovisual en la 
Facultad de Artes del campus Mexicali.

## Documentación
La documentación del sistema se ha elaborado utilizando [Sphinx](https://www.sphinx-doc.org/en/master/). Para generarla,
ejecuta el siguiente comando. Los archivos resultantes se guardarán en `docs/_build`.

- Generar documentación:

  ```sh
  sphinx-build ./docs ./docs/_build/html
  ```

## Pruebas
El proyecto utiliza las herramientas de Django para hacer pruebas unitarias, se recomienda mantener las pruebas 
actualizadas para garantizar una mayor calidad en el código:

- Pruebas unitarias:

    ```sh
    python manage.py test PEMA/tests
    ```

- Cobertura de código:

    ```sh
    coverage run manage.py test PEMA
    coverage report
    ```

## Entorno de Desarrollo
El sistema está desarrollado en Python y Django, se recomienda ampliamente utilizar entornos virtuales. Para comenzar, 
sigue estos pasos:

- Crear entorno virtual:

    ```sh
    python -m venv .venv
    .venv\Scripts\activate
    ```

- Instalar dependencias del proyecto:

    ```
    pip install -r requirements.txt
    ```

- Generar los modelos, permisos y usuarios de prueba:

  ```sh
    python manage.py makemigrations PEMA
    python manage.py migrate
    python manage.py developer_setup
  ```
  
## Datos de Prueba
Aquí va lo de Héctor...
