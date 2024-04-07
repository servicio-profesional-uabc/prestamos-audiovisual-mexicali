from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.views import View
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
from django.contrib import messages
from .models import Orden, User, Prestatario


class IndexView(View):
    def get(self, request):
        return render(
            request=request,
            template_name="index.html"
        )

class MenuView(View):
    def get(self, request):
        matricula = request.user.username
        return render(
            request=request,
            template_name="menu.html",
            context={'matricula':matricula}
        )

    def post(self, request):
        pass


class CarritoView(View):
    def get(self, request):
        return render(
            request=request,
            template_name="carrito.html"
        )

class FiltrosView(View):
    def get(self, request):
        return render(
            request=request,
            template_name="filtros.html"
        )

class SolicitudView(View):
    def get(self, request):
        return render(
            request=request,
            template_name="solicitud.html"
        )



class HistorialSolicitudesView(View):
    def get(self, request):
        prestatario = Prestatario.get_user(request.user)
        print(prestatario)
        solicitudes_pendientes_ap = Orden.objects.filter(prestatario=prestatario, estado=Orden.Estado.PENDIENTE_AP)
        print(solicitudes_pendientes_ap)


#        if solicitudes:
        return render(
            request=request,
            template_name="historial_solicitudes.html",
            context={'solicitudes_pendientes_ap' : solicitudes_pendientes_ap}
        )



class DetallesOrdenView(View):
    def get(self, request, orden_id=None): 
        orden = Orden.objects.get(id=orden_id) if orden_id else None

        return render(
            request=request,
            template_name="detalles_orden.html",
            context={"orden": orden} 
        )
    

class CatalogoView(View):
    def get(self, request):
        return render(
            request=request,
            template_name="catalogo.html"
        )


class DetallesArticuloView(View):
    def get(self, request):
        return render(
            request=request,
            template_name="detalles_articulo.html"
        )


class CancelarOrdenView(View):
    def get(self, request):
        return render(
            request=request,
            template_name="cancelar_orden.html"
        )


def test(request):
    send_mail(
        subject="Email de pruebfrom .forms import LoginForma",
        message="Hola, estoy enviando correos electrónicos desde Django. Si estás recibiendo esto, es porque la "
                "prueba fue exitosa. Atentamente, Galindo.",
        from_email=settings.EMAIL_HOST_USER,
        fail_silently=False,
        recipient_list=[
            "egalindo54@uabc.edu.mx"
        ]
    )

    return HttpResponse("OK")

class RecuperarContrasenaView(View):
    def get(self, request):
        return render(
            request=request,
            template_name="recuperar_contrasena.html"
        )
    
