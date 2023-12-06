from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse

# Create your views here.
def test(request):
    """send_mail(
        subject="Email de prueba",
        message="Hola, estoy enviando correos electrónicos desde Django. Si estás recibiendo esto, es porque la "
                "prueba fue exitosa. Atentamente, Galindo.",
        from_email=settings.EMAIL_HOST_USER,
        fail_silently=False,
        recipient_list=[
            "egalindo54@uabc.edu.mx"
        ]
    )"""
    return HttpResponse("OK")