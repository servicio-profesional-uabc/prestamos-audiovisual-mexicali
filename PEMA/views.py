from django.contrib.auth import authenticate, login
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import get_object_or_404
from django.http import HttpResponseNotAllowed
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseRedirect
from django.views import View
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib import messages

from .forms import FiltrosForm
from .models import Orden, User, Prestatario, EstadoOrden, Materia, Carrito

from .models import Orden, User, Prestatario, Group, Almacen, Coordinador, Entrega, EstadoOrden, AutorizacionOrden, Autorizacion
from django.urls import reverse
from django.shortcuts import redirect
from django.utils import timezone
from django.db import IntegrityError


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
        prestatario = Prestatario.get_user(request.user)

        form = FiltrosForm()
        context = {
            'prestatario':prestatario,
            'form':form,
        }

        return render(
            request=request,
            template_name="filtros.html"
        )

    def post(self, request):
        prestatario = Prestatario.get_user(request.user)
        data = request.POST
        fecha_inicio = request.POST.get('inicio')
        tiempo = request.POST.get('time')
        materias = request.POST.get('materias')

        # if fecha_inicio != "":
        #     pass
        #
        # if request.POST.get('time') == "":
        #     messages.error(request, "FALLO")

        return redirect('filtros')
            # carrito = form.save(commit=False)
            # carrito.prestatario = prestatario
            # carrito.materia = Materia.objects.get(nombre="Iluminacion")
            # carrito.final = carrito.inicio + timedelta(days=3)
            # print(f"xdddddd {carrito.inicio}")

class SolicitudView(View):
    def get(self, request):
        return render(
            request=request,
            template_name="solicitud.html"
        )


class Permisos(View):
    def get(self, request):
        if request.user.is_authenticated:
            nombre_grupo_perteneciente = request.user.groups.first().name
            if nombre_grupo_perteneciente:
                if nombre_grupo_perteneciente == "prestatario":
                    prestatario_group = Group.objects.get(name='prestatarios')
                    permisos = prestatario_group.permissions.all()
                elif nombre_grupo_perteneciente == "maestro":
                    maestro_group = Group.objects.get(name='maestro')
                    permisos = maestro_group.permissions.all()
                elif nombre_grupo_perteneciente == "coordinador":
                    coordinador_group = Group.objects.get(name='coordinador')
                    permisos = coordinador_group.permissions.all()
                elif nombre_grupo_perteneciente == "almacen":
                    almacen_group = Group.objects.get(name='almacen')
                    permisos = almacen_group.permissions.all()


        return render(
            request=request,
            template_name="menu.html",
            context={'grupo': nombre_grupo_perteneciente}
        )


class HistorialSolicitudesView(View):
    def get(self, request):
        prestatario = Prestatario.get_user(request.user)

        try:
            solicitudes_pendientes_ap = Orden.objects.filter(prestatario=prestatario, estado=Orden.Estado.PENDIENTE_AP)
            solicitudes_pendientes_ap.order_by('emision')
        except:
            solicitudes_pendientes_ap = None

        try:
            solicitudes_pendientes_cr = Orden.objects.filter(prestatario=prestatario, estado=Orden.Estado.PENDIENTE_CR)
            solicitudes_pendientes_cr.order_by('emision')
            #print(solicitudes_pendientes_cr.get(lugar=Orden.Ubicacion.EXTERNO))
        except:
            solicitudes_pendientes_cr = None

        try:
            solicitudes_aprobadas = Orden.objects.filter(prestatario=prestatario, estado=Orden.Estado.APROBADA)
            solicitudes_aprobadas.order_by('emision')
        except:
            solicitudes_aprobadas = None

        try:
            solicitudes_rechazadas = Orden.objects.filter(prestatario=prestatario, estado=Orden.Estado.RECHAZADA)
            solicitudes_rechazadas.order_by('emision')
        except:
            solicitudes_rechazadas = None

        try:
            solicitudes_canceladas = Orden.objects.filter(prestatario=prestatario, estado=Orden.Estado.CANCELADA)
            solicitudes_canceladas.order_by('emision')
        except:
            solicitudes_canceladas = None


        context = {'solicitudes_pendientes_ap' : solicitudes_pendientes_ap,
                   'solicitudes_pendientes_cr' : solicitudes_pendientes_cr,
                   'solicitudes_aprobadas' : solicitudes_aprobadas,
                   'solicitudes_rechazadas' : solicitudes_rechazadas,
                   'solicitudes_canceladas' : solicitudes_canceladas,}

        return render(
            request=request,
            template_name="historial_solicitudes.html",
            context=context,
        )



class DetallesOrdenView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        prestatario = Prestatario.get_user(self.request.user)
        orden = get_object_or_404(Orden, id=self.kwargs['id'])
        return prestatario == orden.prestatario

    def get(self, request, id):
        orden = Orden.objects.get(id=id)
        return render(
            request=request,
            template_name="detalles_orden.html",
            context={"orden": orden}
        )

    def post(self, request, id):
        orden = get_object_or_404(Orden, id=id)
        orden.estado = EstadoOrden.CANCELADA
        orden.save()
        messages.success(request, "Haz cancelado tu orden exitosamente.")
        return redirect("historial_solicitudes")


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




    
