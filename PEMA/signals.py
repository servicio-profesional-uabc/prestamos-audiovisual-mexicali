from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.template.loader import render_to_string

from PEMA.models import AutorizacionEstado, Devolucion, Entrega
from PEMA.models import CorresponsableOrden
from PEMA.models import EstadoOrden
from PEMA.models import Orden
from PEMA.models import Perfil
from prestamos import settings


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


@receiver(m2m_changed, sender=Orden._corresponsables.through)
def update_corresponsable_orden(sender, instance, action, *args, **kwargs):
    """
    Actualiza las instancias de CorresponsableOrden cuando cambia la lista de corresponsables de una orden.

    """

    if action == 'post_remove':
        # eliminar todos los CorresponsableOrden que no sean corresponsables
        CorresponsableOrden.objects.exclude(id__in=instance.corresponsables()).delete()

    if action == 'post_add':
        # crear el corresponsableOrden de cada corresponsable y enviar correo
        for item in instance._corresponsables.all():

            object, created = CorresponsableOrden.objects.get_or_create(autorizador=item, orden=instance)

            if created:
                send_mail(
                    subject="Test Email",
                    from_email=settings.EMAIL_HOST_USER,
                    fail_silently=False,
                    message=render_to_string(
                        'emails/aceptar_corresponsable.html',
                        {
                            'invitacion': object,
                            'orden': object.orden,
                            'user': object.autorizador,
                            'host': settings.URL_BASE_PARA_EMAILS,
                        }
                    ),
                    recipient_list=[
                        object.autorizador.email
                    ]
                )


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
