from django.contrib.auth import authenticate, login
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
from .models import Orden, User, Prestatario, Group, Almacen, Coordinador, Entrega, EstadoOrden, AutorizacionOrden, Autorizacion, CorresponsableOrden
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
        orden = Orden.objects.get(id=self.kwargs['id'])
        return prestatario == orden.prestatario

    def get(self, request, id):
        orden = Orden.objects.get(id=id)
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



###################ADMINISTRADOR##########################
class InventarioView(View):
    def get(self, request):
        return render(
            request=request,
            template_name="administrador_permisos/inventario.html"
        )

class UsuariosMateriasView(View):
    def get(self, request):
        return render(
            request=request,
            template_name="administrador_permisos/usuarios_y_materias.html"
        )


######################ALMACEN###############################

#######################VISTA PRINCIPAL#########################
class PrincipalAlmacenView(View):
    def get(self, request):
        ordenes_aprobadas = Orden.objects.filter(estado=EstadoOrden.APROBADA)

        print("ESTOOO",ordenes_aprobadas)  # Comprueba si obtienes resultados aquí

        return render(
            request=request,
            template_name="almacen_permisos/principal.html",
            context={"ordenes": ordenes_aprobadas}
        )


#########ORDENES AUTORIZADAS#############


class DetallesOrdenAutorizadaView(View):
    def get(self, request, id):
        orden = get_object_or_404(Orden, id=id, estado=EstadoOrden.APROBADA)

        return render(
            request=request,
            template_name="almacen_permisos/detalles_orden_autorizada.html",
            context={"orden": orden}
        )



#############ORDENES PRESTADAS#######################
class OrdenesPrestadasView(View):
    def get(self, request):
        ordenes_prestadas = Orden.objects.filter(estado=EstadoOrden.ENTREGADA)
        print("ESTOOO 2",ordenes_prestadas)  # Comprueba si obtienes resultados aquí


        return render(
            request=request,
            template_name="almacen_permisos/ordenes_prestadas.html",
            context={'ordenes': ordenes_prestadas}
        )

class DetallesOrdenPrestadaView(View):
    def get(self, request, id):
        orden = get_object_or_404(Orden, id=id, estado=EstadoOrden.ENTREGADA)


        return render(
            request=request,
            template_name="almacen_permisos/detalles_orden_prestada.html",
            context={"orden": orden}
        )



##################ORDENES REPORTADAS#########################
class OrdenesReportadasView(View):
    def get(self, request):
        ordenes_devueltas = Orden.objects.filter(estado=EstadoOrden.RECHAZADA)
        print("ESTOOO 6",ordenes_devueltas)  # Comprueba si obtienes resultados aquí


        return render(
            request=request,
            template_name="almacen_permisos/ordenes_reportadas.html",
            context={'ordenes': ordenes_devueltas}
        )



class ReportarOrdenView(View):
    def get(self, request, id):
        return render(
            request=request,
            template_name="reportar_orden.html"
        )

class DetallesOrdenReportadaView(View):
    def get(self, request, id):
        orden = get_object_or_404(Orden, id=id, estado=EstadoOrden.RECHAZADA)

        return render(
            request=request,
            template_name="almacen_permisos/detalles_orden_reportada.html",
            context={"orden": orden}
        )



#devolucion = recibir
#prestar = entregar

####################ORDENES DEVUELTAS#######################################
class OrdenesDevueltasView(View):
    def get(self, request):
        ordenes_devueltas = Orden.objects.filter(estado=EstadoOrden.DEVUELTA)
        print("EST 33",ordenes_devueltas)  # Comprueba si obtienes resultados aquí

        return render(
            request=request,
            template_name="almacen_permisos/ordenes_devueltas.html",
            context={'ordenes': ordenes_devueltas}
        )

class DetallesOrdenDevueltaView(View):
    def get(self, request, id):
        orden = get_object_or_404(Orden, id=id, estado=EstadoOrden.DEVUELTA)

        return render(
            request=request,
            template_name="almacen_permisos/detalles_orden_devuelta.html",
            context={"orden": orden}
        )







#########################CORDINADOR########################
class OrdenesReportadasCordinadorView(View):
    def get(self, request):
        return render(
            request=request,
            template_name="coordinador_permisos/ordenes_reportadas_cordi.html"
        )


##################################3
def cambiar_estado_ENTREGADO(request, orden_id, estado):
    if request.method == 'POST':
        orden_id = request.POST.get('orden_id')
        try:
            orden = Orden.objects.get(id=orden_id)
            orden.estado = EstadoOrden.ENTREGADA
            orden.save()
            return redirect('ordenes_prestadas')
        except Orden.DoesNotExist:
            return render(request, 'error.html', {'mensaje': 'La orden no existe'})
    else:
        return render(request, 'error.html', {'mensaje': 'Método no permitido'})

def cambiar_estado_DEVUELTO(request, orden_id, estado):
    if request.method == 'POST':
        orden_id = request.POST.get('orden_id')
        try:
            orden = Orden.objects.get(id=orden_id)
            orden.estado = EstadoOrden.DEVUELTA
            orden.save()
            return redirect('ordenes_devueltas')
        except Orden.DoesNotExist:
            return render(request, 'error.html', {'mensaje': 'La orden no existe'})
    else:
        return render(request, 'error.html', {'mensaje': 'Método no permitido'})