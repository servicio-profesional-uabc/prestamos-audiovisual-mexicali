Email
=====

PEMA utiliza el módulo de `correo electrónico de Django <https://docs.djangoproject.com/en/4.2/topics/email/>`_.

Durante la instalación, es necesario ajustar las credenciales en el archivo ``prestamos/settings.py``. La configuración básica para enviar correos a través de SMTP con Django se presenta así:

.. code-block:: python

    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_HOST_USER = 'tucorreodelprueba@gmail.com'
    EMAIL_HOST_PASSWORD = 'contraseña'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_USE_SSL = False

Contraseñas de aplicación
~~~~~~~~~~~~~~~~~~~~~~~~~

Si usas un correo de Gmail, reemplaza ``EMAIL_HOST_PASSWORD`` con una `contraseña de aplicación <https://support.google.com/accounts/answer/185833?hl=es-419&sjid=12118937065046785513-NC>`_. Para crearla, activa la verificación de dos pasos, ve a "contraseñas de aplicación" en "myaccount", y genera una clave de 16 caracteres (similar a ``octarjvpsyfxuwdg``). Esta clave reemplazará el valor de ``EMAIL_HOST_PASSWORD``.

Backend de correo
~~~~~~~~~~~~~~~~~

- ``django.core.mail.backends.console.EmailBackend`` imprime los correos en la consola de la aplicación.
- ``django.core.mail.backends.smtp.EmailBackend`` envía los correos a través de SMTP.