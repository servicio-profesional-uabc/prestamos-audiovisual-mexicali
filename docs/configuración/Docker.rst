Docker
======

Requisitos
----------

- Instalar docker: `Docker <https://www.docker.com/products/docker-desktop/>`_

Ejecución
---------

Teniendo localmente el repositorio, abre una terminal y posicionate en el directorio que contiene el archivo ``docker-compose.yml``.
Ejecuta este comando para iniciar la base de datos mySQL (db) y la aplicación de Django configurada con Apache2 (app): ``docker-compose up``, Para detenerlos, ejecuta: ``docker-compose down``

.. note::
    La imagen de Django depende de la imagen db. Al ejecutar ``docker-compose``, puedes observar errores, pero esto se debe a que la imagen db no ha terminado. La imagen de la app se estará reiniciando hasta que db haya concluido. Solo es cuestión de esperar a que aparezca este mensaje:

    .. code-block:: console

        db-1  | 2024-03-26T21:52:34.817622Z 0 [System] [MY-010931] [Server] /usr/sbin/mysqld: ready for connections. Version: '8.3.0'  socket: '/var/run/mysqld/mysqld.sock'  port: 3306  MySQL Community Server - GPL.

    Esto significa que ya está listo y la imagen de la app ya reconoce la base de datos.

.. note::

    ``docker-compose.yml``, ``settings.py`` y la configuración de Apache2 están configurados para localhost (ideal para desarrollo).

    Para producción, deberás reemplazar las IPs de localhost/127.0.0.1 en dichos archivos para que apunten al dominio proporcionado. Luego ejecuta ``docker-compose.yml``.

    Siempre ejecuta ``docker-compose down`` al terminar de contribuir y cierra Docker. Docker consume CPU y RAM de tu computadora si lo dejas ejecutándose.

    El volumen de la imagen de mySQL mantiene persistencia en los datos por si llegara a caerse. Esto se ejecuta en ``docker-compose.yml``.
