import os

from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.template.loader import render_to_string

from PEMA.models import AutorizacionEstado, Coordinador, Devolucion, Entrega, TipoOrden
from PEMA.models import AutorizacionOrden
from PEMA.models import CorresponsableOrden
from PEMA.models import EstadoOrden
from PEMA.models import Orden
from PEMA.models import Perfil
from prestamos import settings

#sender: The model class which the signal was called with.
#instance: The instance of a User, whether this was created or updated.
#created: A Boolean to determine if the User was updated or created.
#When the signal is called, none of the parameters will be empty.

@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """
    Crea un perfil asociado a un usuario cada vez que se guarda un usuario nuevo.

    Args:

        sender (Model): User
        instance (User): La instancia de usuario que se está guardando.
        created (bool): Indica si el usuario fue recién creado.
        **kwargs: Parámetros adicionales.

    """

    if not created:
        return

    Perfil.objects.create(usuario=instance)


@receiver(m2m_changed, sender=Orden._corresponsables.through)
def update_corresponsable_orden(sender, instance, action, *args, **kwargs):
    """
    Actualiza las instancias de CorresponsableOrden cuando cambia la lista de corresponsables de una orden.

    Args:
        sender (Model): Orden corresponsable.
        instance (Orden): La instancia de orden que está siendo modificada.
        action (str): La acción que disparó la señal ('post_remove' o 'post_add').
        *args: Argumentos adicionales.
        **kwargs: Parámetros adicionales.
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

    Args:
        sender (Model): CorresponsableOrden
        instance (CorresponsableOrden): La instancia de CorresponsableOrden que está siendo modificada.
        created (bool): Indica si la CorresponsableOrden fue recién creada.
        **kwargs: Parámetros adicionales.

    """

    # TODO: faltan pruebas unitarias para este trigger

    orden = instance.orden

    if created:
        # si el registro se crea, no hace nada
        return

    # si el registro se modifica
    # verificar las respuestas de los corresponsables
    match orden.estado_corresponsables():
        case AutorizacionEstado.ACEPTADA:

            orden.estado = EstadoOrden.RESERVADA  # esperando autorización
            orden.solicitar_autorizacion() # envia solicitud a maestro o coordinador dependiendo del tipo de orden
            # orden.solicitar_autorizacion(orden)  # enviar solicitudes

        case AutorizacionEstado.RECHAZADA:
            orden.estado = EstadoOrden.CANCELADA

    # guardar orden actualizada
    orden.save()


@receiver(post_save, sender=AutorizacionOrden)
def autorizacion_orden_updated(sender, instance, created, **kwargs):
    # TODO: faltan pruebas unitarias para este trigger

    if created:  # si la autorización se crea
        return

    # si la autorización cambia de estado
    # if instance.aceptada():
    #     instance.orden.autorizar()

    # if instance.rechazada():
    #     instance.orden.rechazar()

    # instance.orden.save()


@receiver(post_save, sender=AutorizacionOrden)
def autorizacion_orden_created(sender, instance, created, **kwargs):
    """
    Esta señal se activa al crear una AutorizacionOrden y envía un correo electrónico al maestro o coordinador para que aprueben
    o cancelen la orden correspondiente. Además, se crean los objetos de AutorizacionOrden mediante la llamada
    a orden.solicitar_autorizacion() dentro de la señal corresponsable_orden_updated.


    Args:
        sender (Model): AutorizacionOrden
        instance (AutorizacionOrden): La instancia de AutorizacionOrden que está siendo modificada.
        created (bool): Indica si la AutorizacionOrden fue recién creada.
        **kwargs: Parámetros adicionales.
    """
    if not created:  # se crea una autorización
        return

    orden = instance.orden

    autorizador = instance.autorizador
    prestatario = instance.orden.prestatario    

    send_mail(
        subject=f"PEMA - Nueva solicitud de autorización para préstamo de equipo",
        from_email=settings.EMAIL_HOST_USER,
        fail_silently=False,
        message=render_to_string(
            'emails/aprobar_solicitud.html',
            {
                'orden': orden,
                'user': prestatario,
                'autorizador': autorizador,
                'host': settings.URL_BASE_PARA_EMAILS,
            }
        ),
        recipient_list=[autorizador.email]
    )


@receiver(post_save, sender=Entrega)
def entrega_created(sender, instance, created, **kwargs):
    """
    Esta señal se dispara cuando un usuario del almacén crea una entrega desde la interfaz de administración,
    restringida solo a usuarios del almacén. Para que la entrega sea válida, la orden debe estar en estado APROBADA,
     lo que indica que está lista para comenzar en la fecha y hora programadas. La función entregar() verifica este estado antes
    de crear la instancia de Entrega.

    Args:
        sender (Model): Entrega
        instance (Entrega): La instancia de Entrega que está siendo creada.
        created (bool): Indica si la Entrega fue recién creada.
        **kwargs: Parámetros adicionales.
    """
    if not created:
        return
    
    orden = instance.orden
    entregador = instance.entregador
    orden.entregar(entregador)

@receiver(post_save, sender=Devolucion)
def devolucion_created(sender, instance, created, **kwargs):
    """
    Esta señal se activa cuando un usuario del almacén crea una devolución desde la interfaz de administración,
    con acceso restringido exclusivamente a usuarios del almacén. Para que la devolución pueda realizarse, la orden debe estar
    en estado ENTREGADA. La función devolver() verifica este estado antes de crear la instancia de Devolución.


    Args:
        sender (Model): Devolucion
        instance (Devolucion): La instancia de Devolucion que está siendo creada.
        created (bool): Indica si la Devolucion fue recién creada.
        **kwargs: Parámetros adicionales.
    """
    if not created:
        return

    orden = instance.orden
    almacen = instance.almacen
    orden.devolver(almacen)
