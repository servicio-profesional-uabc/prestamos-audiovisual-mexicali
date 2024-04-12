# Sistema de Gestión de Préstamos de Material Audiovisual (PEMA)

PEMA es una herramienta diseñada para simplificar la gestión de préstamos de material de grabación audiovisual en la Facultad de Artes del campus Mexicali.

## Documentación

La documentación del sistema se ha elaborado utilizando Sphinx. Para generarla, ejecuta el siguiente comando. Los archivos resultantes se guardarán en `docs/_build`.

```sh
sphinx-build ./docs ./docs/_build/html
```

## Pruebas
### Ejecución de Pruebas

Para ejecutar las pruebas unitarias, utiliza el siguiente comando:

```sh
python manage.py test PEMA/tests
```

### Cobertura de Código

Para obtener un informe de cobertura de código, sigue los siguientes pasos:

1. Generar la información sobre las pruebas:   
   ```sh
   coverage run --source='./PEMA' manage.py test PEMA
   ```

2. Mostrar el reporte en la terminal:
   ```sh
   coverage report
   ```

## Entorno de Desarrollo

El sistema está desarrollado en Python y Django. Para comenzar, sigue estos pasos:

1. Instala las dependencias necesarias utilizando el siguiente comando:
   
   ```sh
   pip install -r requirements.txt
   ```

2. Realiza las migraciones de la base de datos ejecutando los siguientes comandos:
   
   ```sh
   python manage.py makemigrations PEMA
   python manage.py migrate
   ```

3. Configura los roles del sistema con:
   
   ```sh
   python manage.py crear_roles
   ```

4. Prepara el entorno de desarrollo con:
   
   ```sh
   python manage.py developer_setup
   ```

5. Finalmente, inicia el servidor local con:
   
   ```sh
   python manage.py runserver
   ```