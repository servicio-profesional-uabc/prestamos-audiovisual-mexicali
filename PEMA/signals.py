from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from PEMA.models import Perfil, CorresponsableOrden, Orden, Maestro, Coordinador, EstadoOrden, AutorizacionOrden


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """
    Esta función se ejecuta cada vez que se guarda un usuario.

    Crea un perfil asociado a ese usuario, el cual contiene información
    adicional para el modelo estándar de usuario de Django. Para obtener
    más detalles sobre qué datos contiene este perfil, revisa el modelo
    `Perfil`.
    """
    if not created:
        return
    Perfil.objects.create(usuario=instance)


@receiver(post_save, sender=CorresponsableOrden)
def corresponsable_orden_updated(sender, instance, created, **kwargs):
    """
    Esta función se ejecuta cada vez que se actualiza un CorresponsableOrden.

    Durante esta actualización, se verifica el estado de la orden. Para
    que la orden sea aprobada, todos los corresponsables deben aceptarla
    y ninguno debe haberla rechazado. Si la orden es aceptada, se envía
    una solicitud de autorización al profesor si la orden es de tipo
    ordinaria, o al coordinador si es de tipo extraordinaria.
    """

    # TODO: faltan pruebas unitarias para este trigger

    orden = instance.orden
    estado = CorresponsableOrden.Estado

    if created:
        # si el registro se crea
        return

    # TODO: bloquear el estado una vez que se rechaze o acepte

    # verificar las respuestas de los corresponsables
    match orden.estado_corresponsables():
        case estado.ACEPTADA:  # Si todos aceptaron

            # cambiar estado `pendiente corresponsables` a `pendiente autorizacion`
            orden.estado = EstadoOrden.PENDIENTE_AP

            # solicitar las autorizaciones
            if orden.es_ordinaria():
                Maestro.solicitar_autorizacion(orden)

            if orden.es_extraordinaria():
                Coordinador.solicitar_autorizacion(orden)

        case estado.RECHAZADA:  # Si alguno rechazo
            orden.estado = EstadoOrden.RECHAZADA

    # guardar orden actualizada
    orden.save()


@receiver(post_save, sender=AutorizacionOrden)
def autorizacion_orden_updated(sender, instance, created, **kwargs):
    # TODO: faltan pruebas unitarias para este trigger

    if created: # si la autorización cambia de estado
        return

    autorizacion = instance
    orden = instance.orden

    # TODO: bloquear el estado una vez que se rechaze o acepte

    if autorizacion.aceptada():
        orden.estado = EstadoOrden.APROBADA

    if autorizacion.rechazada():
        orden.estado = EstadoOrden.RECHAZADA

    orden.save()


@receiver(post_save, sender=AutorizacionOrden)
def autorizacion_orden_created(sender, instance, created, **kwargs):
    if not created: # se crea una autorizacion
        return

    orden = instance.orden

    send_mail(subject="Email de pruebfrom .forms import LoginForma",
              message="Hola, estoy enviando correos electrónicos desde Django. Si estás recibiendo esto, es porque la "
                      "prueba fue exitosa. Atentamente, Galindo.", from_email=settings.EMAIL_HOST_USER,
              fail_silently=False, recipient_list=["egalindo54@uabc.edu.mx"])


post_save.connect(user_post_save, sender=User)
post_save.connect(corresponsable_orden_updated, sender=CorresponsableOrden)
post_save.connect(autorizacion_orden_created, sender=AutorizacionOrden)
post_save.connect(autorizacion_orden_updated, sender=AutorizacionOrden)
