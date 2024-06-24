from django.contrib.auth.models import User
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from PEMA.models import AutorizacionEstado, Devolucion, Entrega
from PEMA.models import CorresponsableOrden
from PEMA.models import Orden
from PEMA.models import Perfil


# sender: The model class which the signal was called with.
# instance: The instance of a User, whether this was created or updated.
# created: A Boolean to determine if the User was updated or created.
# When the signal is called, none of the parameters will be empty.

@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """
    Crea un perfil asociado a un usuario cada vez que se guarda un usuario nuevo.
    """

    if not created:
        return

    Perfil.objects.create(usuario=instance)


@receiver(post_save, sender=Orden)
def orden_after_create(sender, instance, created, **kwargs):
    if created:
        instance.agregar_corresponsable(instance.prestatario)
        instance.notificar_corresponsables()


@receiver(post_save, sender=CorresponsableOrden)
def corresponsable_orden_updated(sender, instance, created, **kwargs):
    """
    Esta función se activa cuando se modifica un registro de CorresponsableOrden.
    Verifica si todos los corresponsables han aceptado la orden y ninguno la ha rechazado para que pueda ser aprobada.
    En caso de ser aprobada, se envía una solicitud de autorización al profesor (si la orden es ordinaria) o al coordinador
    (si es extraordinaria). Además, actualiza el estado de la orden según los cambios en CorresponsableOrden.

    """

    # TODO: faltan pruebas unitarias para este trigger

    orden = instance.orden

    if created:
        # si el registro se crea, no hace nada
        return

    # si el registro se modifica
    # Estado de los corresponsables, si aceptan la orden o no
    estado_corresponsables = orden.estado_corresponsables()

    if estado_corresponsables == AutorizacionEstado.ACEPTADA:
        # si todos aceptan se envia la solicitud al maestro/coordinador
        orden.solicitar_autorizacion()

    if estado_corresponsables == AutorizacionEstado.RECHAZADA:
        # si alguno cancela la solicitud se cancela
        orden.cancelar()


@receiver(post_save, sender=Entrega)
def entrega_created(sender, instance, created, **kwargs):
    """
    Actualiza automáticamente el estado de la orden asociada a "Entregado" cada vez que se crea una nueva instancia de Entrega.

    El sistema verifica si esta entrega es nueva o si es una actualización de una existente.
    Si es una entrega nueva , se marcar la orden relacionada como entregada.
    Utiliza la información del entregador que realizó la entrega para actualizar el estado de la orden,
    indicando que ha sido entregada satisfactoriamente.


    """
    if not created:
        return

    orden = instance.orden
    entregador = instance.entregador
    orden.entregar(entregador)


@receiver(post_save, sender=Devolucion)
def devolucion_created(sender, instance, created, **kwargs):
    """
    La señal devolucion_created se activa cada vez que se guarda una instancia del modelo Devolucion en el sistema.

    Se verifica si la instancia de Devolucion acaba de ser creada.
    Obtener la orden asociada a la devolución.
    Realizar operaciones relacionadas con la devolución de la orden.
    """
    if not created:
        return

    orden = instance.orden
    almacen = instance.almacen
    orden.devolver(almacen)
