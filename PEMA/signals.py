from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from PEMA.models import Perfil, CorresponsableOrden, Orden, Maestro, Coordinador


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
    orden: Orden = instance.orden
    estado = CorresponsableOrden.Estado

    # verificar las respuestas de los corresponsables
    match orden.estado_corresponsables():
        case estado.ACEPTADA:  # Si todos aceptaron

            # cambiar estado `pendiente corresponsables` a `pendiente autorizacion`
            orden.estado = Orden.Estado.PENDIENTE_AP

            if orden.es_ordinaria():
                Maestro.solicitar_autorizacion(orden)
            else:
                Coordinador.solicitar_autorizacion(orden)

        case estado.RECHAZADA:  # Si alguno rechazo
            orden.estado = Orden.Estado.RECHAZADA

        case estado.PENDIENTE:  # Si todavía falta alguno de aceptar
            orden.estado = Orden.Estado.PENDIENTE_CR

    # guardar orden actualizada
    orden.save()


post_save.connect(user_post_save, sender=User)
post_save.connect(corresponsable_orden_updated, sender=CorresponsableOrden)
