Base de datos
=============

mySQL
-----

Para establecer la conexión, es necesario tener `PyMySQL
<https://pypi.org/project/pymysql/>`_ instalado. 

Instalar PyMySQL
~~~~~~~~~~~~~~~~

En el proyecto, localiza el archivo ``__init__.py`` que se encuentra
en el mismo directorio que ``settings.py`` y copia las siguientes
líneas: 

.. code-block:: python

    import pymysql
    pymysql.install_as_MySQLdb()

Crear el esquema
~~~~~~~~~~~~~~~~

Después, crea el esquema de la base de datos en mySQL:

.. code-block:: sql

    CREATE SCHEMA `new_schema`;

Crear la configuración
~~~~~~~~~~~~~~~~~~~~~~

Por último, en el archivo ``settings.py``, ve a la sección de
``DATABASES`` y agrega la información de la conexión: 

.. code-block:: python

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'NOMBRE ESQUEMA',
            'USER': 'USUARIO',
            'PASSWORD': 'CONTRASEÑA',
            'HOST': 'localhost',
            'PORT': '3306',
        }
    }

Migraciones
~~~~~~~~~~~

Una vez establecida la conexión, podemos importar los modelos del
proyecto: 

.. code-block:: sh

    python manage.py makemigrations PEMA
    python manage.py migrate
