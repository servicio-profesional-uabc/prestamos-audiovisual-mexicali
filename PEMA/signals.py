import os

from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.template.loader import render_to_string

from PEMA.models import AutorizacionEstado, Coordinador, Entrega, TipoOrden
from PEMA.models import AutorizacionOrden
from PEMA.models import CorresponsableOrden
from PEMA.models import EstadoOrden
from PEMA.models import Orden
from PEMA.models import Perfil
from prestamos import settings


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
    Esta señal se ejecuta cada vez que se crea una autorización, este envía un correo al usuario maestro o coordinador para aprobar o cancelar dicha orden.
    orden.solicitar_autorizacion() se crean dichos objetos de AutorizacionOrden (esto sucede en la señal corresponsable_orden_updated)
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
    Esta señal se ejecuta cada vez que el usuario Almacen crea una entrega en la vista de /admin modificado a permisos solo para un usuario Almacen.
    Una entrega solo es posible si la orden esta en estado de APROBADA (Listo para iniciar para la fecha y hora de inicio).
    """
    if not created:
        return
    
    orden = instance.orden
    entregador = instance.entregador
    orden.entregar(entregador)
