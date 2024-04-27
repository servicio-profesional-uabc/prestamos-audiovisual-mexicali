from django.contrib.auth.models import User
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from PEMA.models import AutorizacionEstado
from PEMA.models import AutorizacionOrden
from PEMA.models import CorresponsableOrden
from PEMA.models import EstadoOrden
from PEMA.models import Orden
from PEMA.models import Perfil


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """
    Esta señal se ejecuta cada vez que se guarda un usuario.

    Crea un perfil asociado a ese usuario, el cual contiene información
    adicional para el modelo estándar de usuario de Django.
    """
    if not created:
        return

    Perfil.objects.create(usuario=instance)


@receiver(m2m_changed, sender=Orden._corresponsables.through)
def update_corresponsable_orden(sender, instance, action, *args, **kwargs):
    """
    Esta señal se ejecuta cada vez que un corresponsable se actualiza la
    lista de corresponsables de una orden.
    """

    if action == 'post_add':
        # crear el corresponsableOrden de cada corresponsable
        for item in instance._corresponsables.all():
            CorresponsableOrden.objects.get_or_create(prestatario=item, orden=instance)

    if action == 'post_remove':
        # eliminar todos los CorresponsableOrden que no sean corresponsables
        CorresponsableOrden.objects.exclude(id__in=instance.corresponsables()).delete()


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

    if created:
        # si el registro se crea
        return

    # verificar las respuestas de los corresponsables
    match orden.estado_corresponsables():
        case AutorizacionEstado.ACEPTADA:

            orden.estado = EstadoOrden.PENDIENTE_AP  # esperando autorización
            orden.solicitar_autorizacion(orden)  # enviar solicitudes

        case AutorizacionEstado.RECHAZADA:
            orden.estado = EstadoOrden.CANCELADA

    # guardar orden actualizada
    orden.save()


@receiver(post_save, sender=AutorizacionOrden)
def autorizacion_orden_updated(sender, instance, created, **kwargs):
    # TODO: faltan pruebas unitarias para este trigger

    if created:  # si la autorización cambia de estado
        return

    if instance.aceptada():
        instance.orden.autorizar()

    if instance.rechazada():
        instance.orden.rechazar()

    instance.orden.save()


@receiver(post_save, sender=AutorizacionOrden)
def autorizacion_orden_created(sender, instance, created, **kwargs):
    if not created:  # se crea una autorización
        return

    orden = instance.orden
