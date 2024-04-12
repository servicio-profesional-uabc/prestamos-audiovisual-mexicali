Entorno de Desarrollo
=====================

Linux (Ubuntu)
--------------

.. code-block:: sh

   # Clonar el repositorio
   git clone https://github.com/servicio-profesional-uabc/prestamos-audiovisual-mexicali.git
   cd prestamos-audiovisual-mexicali/

   # Crear el entorno virtual
   python3.10 -m venv .venv
   source .venv/bin/activate

   # Instalar las dependencias
   pip install -r requirements.txt

Windows
-------

.. code-block:: sh

   # Clonar el repositorio
   git clone https://github.com/servicio-profesional-uabc/prestamos-audiovisual-mexicali.git
   cd prestamos-audiovisual-mexicali/

   # Crear el entorno virtual
   python -m venv .venv
   .\.venv\Scripts\activate

   # Instalar las dependencias
   pip install -r requirements.txt

Migraciones y datos de prueba
------------------------------

Ejecuta los siguientes comandos para realizar migraciones y cargar datos de prueba:

.. code-block:: sh

   # Migrar los modelos
   python manage.py makemigrations PEMA
   python manage.py migrate

   # Crear los grupos de permisos
   python manage.py crear_roles

   # Crear un superusuario de prueba
   python manage.py developer_setup

Pruebas
-------

Para ejecutar las pruebas, utiliza el siguiente comando:

.. code-block:: sh

   python manage.py test PEMA/tests
