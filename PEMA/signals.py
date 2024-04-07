from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from PEMA.models import Perfil, CorresponsableOrden, Orden, AutorizacionOrdinaria


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """
    Esta función se ejecuta cada vez que se guarda un usuario.

    Crea un perfil asociado a ese usuario, el cual contiene información
    adicional para el modelo estándar de usuario de Django. Para obtener
    más detalles sobre qué datos contiene este perfil, revisa el modelo
    PEMA.Perfil.
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

    if created:  # si el registro se crea
        return

    # si el registro se actualiza
    orden = instance.orden

    match orden.estado_corresponsables():
        case CorresponsableOrden.Estado.PENDIENTE:
            # Si todavía faltán corresponsables de aceptar
            orden.estado = Orden.Estado.PENDIENTE_CR

        case CorresponsableOrden.Estado.RECHAZADA:
            # Sí alguno de los cooresponsables rechazo la orden
            orden.estado = Orden.Estado.RECHAZADA

        case CorresponsableOrden.Estado.ACEPTADA:
            # Si todos los corresponsables aceptaron
            orden.estado = Orden.Estado.PENDIENTE_AP

            # TODO: Falta identificar al Maestro de una clase
            # TODO: Falta identificar al Coordinador

            # TODO: enviar correo de autorizacion a quien corresponda

    orden.save()


post_save.connect(user_post_save, sender=User)
post_save.connect(corresponsable_orden_updated, sender=CorresponsableOrden)
