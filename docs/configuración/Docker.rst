Docker
======

Requisitos
----------
Instalar docker

- Docker en Windows (por si deseas ejecutarlo únicamente para desarrollo)
`Docker Desktop para Windows <https://www.docker.com/products/docker-desktop/>`_

- Docker para ambiente de producción (servidor Linux/Ubuntu)
`Docker Engine para Ubuntu <https://docs.docker.com/engine/install/ubuntu/>`_

.. note:: 
    - Docker Desktop en Linux existe, pero corre en una máquina virtual y no se utiliza para producción.
    - Se recomienda simplemente instalar Docker Engine con el link indicado si estás en Ubuntu Linux y/o en servidor de producción.
    - Docker Engine es la versión de Docker para servidores Linux a través de comandos de terminal. 


Ejecución para Producción
-------------------------
Asegurate que ``wsgi.py`` y ``manage.py`` utilicen el archivo settings de producción ``prestamos/prod.py`` debe decir de esta forma:

.. code-block:: python

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prestamos.prod')

Puntos importantes a considerar antes de ejecutar la aplicación:

.. note::
    - Las siguientes instrucciones corren docker-compose con settings para producción en la aplicación Django.
    - El servidor de producción proporcionada por UABC Mexicali es una máquina virtual con Ubuntu.
    - El archivo docker-compose.yml corre un contenedor llamado pema-app con un servidor Apache2 con Django.
    - Asegurate que toda contraseña creada sea segura y diferente.


.. note::
    Antes de ejecutar cualquier cosa, es necesario configurar las variables necesarias para la crear la imagen de mysql en el archivo ``docker-compose.yml``.
    
    .. code-block:: yaml

        environment:
            MYSQL_ROOT_PASSWORD: ${DATABASE_PASSWORD} 
            MYSQL_DATABASE: ${DATABASE_NAME} 
            MYSQL_USER: 'admin' 
            MYSQL_PASSWORD: ${DATABASE_PASSWORD} 

    El archivo ``docker-compose.yml`` requiere de las variables ambientes en un archivo llamado ``.env`` en el mismo directorio donde ``docker-compose.yml`` se encuentra.
    Este archivo debe contener las siguientes variables:

    .. code-block:: python

        SECRET_KEY='CLAVESECRETA' # La clave secreta de la aplicación de Django (ejemplo)
        APP_RUN_HOST='192.168.191.113' # Public IP de la máquina donde se ejecutará la aplicación (ejemplo de la máquina host)
        APP_RUN_DOMAIN='www.example.com' # Dominio de la aplicación 
        DATABASE_NAME='pema-db' # Nombre de la base de datos (dejar así)
        DATABASE_PASSWORD='P@ssword123' # Contraseña para user root (ejemplo)
        EMAIL='pruebasprestamosmexicali@gmail.com' # Correo por donde se enviaran los correos automatizados (ejemplo)
        EMAIL_PASSWORD='P@ssword123' # Contraseña del correo de donde se enviaran (ejemplo)

Teniendo localmente el repositorio, abre una terminal y posicionate en el directorio que contiene el archivo ``docker-compose.yml``.
Para iniciar la base de datos mySQL (db) con su volumen para la persistencia de datos, y la aplicación de Django configurada con Apache2 (app) ejecuta: ``docker-compose up``, Para detenerlos, ejecuta: ``docker-compose down``

.. note::
    El contenedor app depende del contenedor db. Al ejecutar ``docker-compose up``, puedes observar errores inicialmente, pero esto se debe a que db no ha terminado de crear la base de datos y app no puede hacer conexiones a la db por lo mismo. La app se estará reiniciando hasta que db haya concluido. Solo es cuestión de esperar a que aparezca algo relacionado a ``ready for connections``:

    .. code-block:: console

        db-1  | 2024-03-26T21:52:34.817622Z 0 [System] [MY-010931] [Server] /usr/sbin/mysqld: ready for connections. Version: '8.3.0'  socket: '/var/run/mysqld/mysqld.sock'  port: 3306  MySQL Community Server - GPL.

    Esto significa que ya está listo el contenedor db y app ya debería de reconocer db.

.. note::
    Si creas un contenedor de base de datos, y cae o se detiene el contenedor, los datos de la base de datos se perderán. 
    Para evitar esto, se manda a crear un volumen en el archivo ``docker-compose.yml`` llamado mysql_data, este crea el volumen llamado prestamos-audiovisual-mexicali_mysql_data.

.. danger::
    - Se perderá toda información de la base de datos si se elimina el volumen prestamos-audiovisual-mexicali_mysql_data.
    - En caso de que sea necesario eliminar el volumen, ejecuta: ``docker-compose down`` para parar la aplicación entera y ``docker volume rm prestamos-audiovisual-mexicali_mysql_data`` para eliminar el volumen.

.. note::
    - Para crear usuarios admin para la aplicación de Django, o quieres ejecutar comandos de la app de Django puedes entrar al contenedor mediante ``docker exec -it pema-app bash`` siempre y cuando este corriendo dicho contenedor.
    - Para entrar a la base de datos, puedes ejecutar ``docker exec -it pema-db bash`` y luego ``mysql -u root -p``, te va pedir ingresar la contraseña para root que hayas configurado cuando creaste al contenedor de la base de datos (db) por primera vez. O bien entrar desde /admin para visualizar y manipular los datos (recomendable).


