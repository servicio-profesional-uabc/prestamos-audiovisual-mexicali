from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views import View
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.hashers import check_password
from .forms import LoginForm
from .models import User
from .models import Orden
from django.template import loader


class IndexView(View):
    def get(self, request):
        return render(
            request=request,
            template_name="index.html"
        )


class LoginView(View):
    def get(self, request):
        return render(
            request=request,
            template_name="login.html"
        )

    def post(self, request):
        login_url = 'login'
        menu_url = 'menu'

        matricula = request.POST['matricula']
        password = request.POST['password']

        # Autenticacion
        user = authenticate(request, username=matricula, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Has iniciado sesión!')
            return redirect(menu_url)
        else:
            messages.error(request, 'Hubo un error en los datos que ingreso, intente de nuevo...')
            return redirect(login_url)


class MenuView(View):
    def get(self, request):
        return render(
            request=request,
            template_name="menu.html"
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
        solicitudes = Orden.objects.all() 
        return render(
            request=request,
            template_name="historial_solicitudes.html",
            context={'solicitudes': solicitudes}  
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
