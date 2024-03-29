from django.shortcuts import render
from django.views import View
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
from django.template import loader


class IndexView(View):
    def get(self, request):
        return render(
            request=request,
            template_name="index.html"
        )


class TestView(View):
    def get(self, request):
        return render(
            request=request,
            template_name="test.html"
        )
class PrestatarioView(View):
    def get(self, request):
        return render(
            request=request,
            template_name="prestatario.html"
        )   

class CarritoView(View):
    def get(self, request):
        return render(
            request=request,
            template_name="carrito.html"
        )   

class SolicitudView(View):
    def get(self, request):
        return render(
            request=request,
            template_name="solicitud.html"
        )
    
class HistorialSolicitudesView(View):
    def get(self, request):
        return render(
            request=request,
            template_name="historial_solicitudes.html"
        )
    
class DetallesOrdenView(View):
    def get(self, request):
        return render(
            request=request,
            template_name="detalles_orden.html"
        )


class CatalogoView(View):
    def get(self, request):
        return render(
            request=request,
            template_name="catalogo.html"
        )


class HistorialView(View):
    def get(self, request):
        return render(
            request=request,
            template_name="historial.html"
        )

class DetalleArticuloView(View):
    def get(self, request):
        return render(
            request=request,
            template_name="detalleArticulo.html"
        )

class CancelarOrdenView(View):
    def get(self, request):
        return render(
            request=request,
            template_name="cancelarOrden.html"
        )

def test(request):
    send_mail(
        subject="Email de prueba",
        message="Hola, estoy enviando correos electrónicos desde Django. Si estás recibiendo esto, es porque la "
                "prueba fue exitosa. Atentamente, Galindo.",
        from_email=settings.EMAIL_HOST_USER,
        fail_silently=False,
        recipient_list=[
            "egalindo54@uabc.edu.mx"
        ]
    )

    return HttpResponse("OK")
