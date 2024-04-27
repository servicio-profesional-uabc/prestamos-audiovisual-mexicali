from django.contrib.auth import authenticate, login
from datetime import timedelta, datetime, date
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import get_object_or_404
from django.http import HttpResponseNotAllowed
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseRedirect
from django.utils.timezone import make_aware
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


INICIO_HORARIO = 7
FIN_HORARIO = 20

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

class FiltrosView(View, LoginRequiredMixin):
    def get(self, request):
        prestatario = Prestatario.get_user(request.user)

        form = FiltrosForm(prestatario)

        return render(
            request=request,
            context={'prestatario': prestatario, 'form': form},
            template_name="filtros.html",
        )

    def post(self, request):
        print(request.POST)
        prestatario = Prestatario.get_user(request.user)

        form = FiltrosForm(prestatario, request.POST)
        if form.is_valid():
            materia = form.cleaned_data['materia']
            duracion = form.cleaned_data['duracion']
            inicio = form.cleaned_data['inicio']
            hora_inicio = form.cleaned_data['hora_inicio']

            # [x] Agregar fecha inicio agregarle su hora de inicio
            # [x] Sumarle la duracion de horas a dicha fecha
            # [X] Validar que sea elegido en fecha sea 3 dias de anticipacion
            # [X] Validar que inicio sea entre semana (no importa que pase por fin eso se hace extra al hacer solicitud)
            # [X] Guardar dicha fecha final en la variable final de carrito

            # Si es Sabado o Domingo mostrar error
            if inicio.date().weekday() >= 5:
                messages.error(request, "Por favor elija fecha de inicio de préstamo entre semana.")
                return redirect('filtros')

            # Si fecha de inicio de préstamo es antes de los tres días de anticipación mostrar error.
            if inicio.date() < date.today() + timedelta(days=3):
                messages.error(request, "Por favor elija una fecha tres días a partir de hoy.")
                return redirect('filtros')

            hora_inicio_datetime = datetime.strptime(hora_inicio, '%H:%M:%S')

            # Asignar hora elegida a fecha de inicio
            hora = datetime.time(hora_inicio_datetime)
            fecha_inicio = datetime.combine(inicio, hora)

            tiempo_duracion = int(duracion)

            fecha_final = fecha_inicio + timedelta(hours=tiempo_duracion)
            fecha_final = make_aware(fecha_final)

            # Si es dentro del horario de atención
            if not (INICIO_HORARIO <= fecha_final.time().hour <= FIN_HORARIO):
                messages.error(request, 'La combinación de hora y duración del préstamo marcan fuera de horario de atención. Intente de nuevo.')
                return redirect('filtros')

            if fecha_final.date().weekday() >= 5:
                messages.error(request, 'La fecha de devolución del préstamo es en fin de semana. Intente de nuevo cambiándo la duración del préstamo.')
                return redirect('filtros')

            carrito, created = Carrito.objects.get_or_create(
                prestatario=prestatario,
                materia=materia,
                inicio=fecha_inicio,
                final=fecha_final,
            )
            print(carrito, created)
            messages.success(request, 'El filtro para tu orden se ha creado exitosamente.')
            return redirect('filtros')
        else:
            # Verificar que se eligieron todos los campos antes de guardar
            print(form.errors)
            messages.error(request, "Error al generar tu filtro. Verifica que hayas seleccionado todos los campos.")
            for field, errors in form.errors.items():
                messages.error(request, f"Field: {field}, Errors: {errors}")

            return redirect('filtros')
            for field, errors in form.errors.items():
                print(f"Field: {field}, Errors: {errors}")
        return redirect('filtros')

        # if (fecha_inicio == "" or fecha_inicio == None) or \
        #     (duracion == "" or duracion == None) or \
        #     (materia == "" or materia == None):
        #     if fecha_inicio == "" or fecha_inicio == None:
        #         messages.error(request, "No puedes dejar vacío el campo de fecha.")
        #     if duracion == "" or duracion == None:
        #         messages.error(request, "No puedes dejar vacío el campo de duración.")
        #     if materia == "" or materia == None:
        #         messages.error(request, "No puedes dejar vacío el campo de materia. Si no aparecen tus materias contacta al administrador.")
        #     return redirect('filtros')


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




    
