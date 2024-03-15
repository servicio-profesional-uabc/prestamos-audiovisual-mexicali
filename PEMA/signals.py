from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from PEMA.models import Perfil


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """
    Se crea un perfil para cada usuario
    """
    if created:
        Perfil.objects.create(
            usuario=instance
        )


post_save.connect(user_post_save, sender=User)
