from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.timezone import make_aware
from django.views import View

from .forms import FiltrosForm, ActualizarPerfil, UpdateUserForm
from .models import Carrito, Articulo, Categoria, CorresponsableOrden
from .models import Orden, Prestatario, EstadoOrden, Perfil


class IndexView(View):
    def get(self, request):
        return render(
            request=request,
            template_name="index.html"
        )


class ActualizarPerfilView(LoginRequiredMixin, View):
    """
    Vista para registrar los datos faltantes del usuario
    """

    def get(self, request):
        return render(
            request=request,
            template_name="actualizar_perfil_y_usuario.html",
            context={
                'form_actualizar_perfil': ActualizarPerfil(),
                'form_actualizar_usuario': UpdateUserForm(),
            }
        )

    def post(self, request):
        perfil = Perfil.user_data(user=request.user)

        perfil_form = ActualizarPerfil(request.POST, instance=perfil)
        usuario = UpdateUserForm(request.POST, instance=request.user)

        if perfil_form.is_valid() and usuario.is_valid():
            perfil_form.save()
            usuario.save()
            return redirect('menu')

        return render(
            request=request,
            template_name="actualizar_perfil_y_usuario.html",
            context={
                'form_actualizar_perfil': perfil_form,
                'form_actualizar_usuario': usuario,
            }
        )


class MenuView(View, LoginRequiredMixin):
    def get(self, request):
        # Todos los usaurios deben tener perfil
        # TODO: pantalla de error si no existe el Pefil
        datos_usuario = Perfil.user_data(user=request.user)

        if datos_usuario.incompleto():
            # el usuario tiene datos incompletos
            return redirect('actualizar_perfil')

        return render(
            request=request,
            template_name="menu/menu.html",
            context={'matricula': request.user.username, 'user': request.user}
        )

    def post(self, request):
        pass


class CarritoView(LoginRequiredMixin, UserPassesTestMixin, View):

    def test_func(self):
        prestatario = Prestatario.get_user(self.request.user)
        return prestatario.tiene_carrito()

    def get(self, request, accion=None):
        prestatario = Prestatario.get_user(request.user)
        carrito = prestatario.carrito()

        if accion == 'ordenar':
            # TODO: Mostrar que articulos esta ocupado
            ordenado = carrito.ordenar()

            if ordenado:
                return redirect("historial_solicitudes")

        return render(
            request=request,
            template_name="carrito.html",
            context={
                "articulos_carrito": carrito.articulos_carrito(),
                "carrito": carrito
            }
        )


class FiltrosView(LoginRequiredMixin, View):

    def get(self, request):
        prestatario = Prestatario.get_user(request.user)

        if prestatario.tiene_carrito():
            # Si ya hay un carrito se borra
            prestatario.carrito().eliminar()

        return render(
            request=request,
            template_name="filtros.html",
            context={
                'prestatario': prestatario,
                'form': FiltrosForm(),
                'materias': prestatario.materias(),
            },
        )

    def post(self, request):
        prestatario = Prestatario.get_user(request.user)
        form = FiltrosForm(request.POST)

        if prestatario.tiene_carrito():
            # Si ya hay un carrito se borra
            prestatario.carrito().eliminar()

        if form.is_valid():
            # crear carrito
            inicio = form.cleaned_data.get('inicio')
            hora_inicio = form.cleaned_data.get('hora_inicio')
            duracion = form.cleaned_data.get('duracion')

            # se crea un nuevo carrito
            carrito_nuevo = form.save(commit=False)
            carrito_nuevo.prestatario = request.user

            # TODO: Enhancement - Realizar estas operaciones en sus propios métodos de Carrito
            tiempo_duracion = int(duracion)
            fecha_inicio = datetime.combine(inicio, hora_inicio)

            # Guardar fechas actualizadas
            carrito_nuevo.inicio = make_aware(fecha_inicio)
            carrito_nuevo.final = make_aware(fecha_inicio + timedelta(hours=tiempo_duracion))

            carrito_nuevo.save()
            return redirect("catalogo")

        return render(
            request=request,
            template_name="filtros.html",
            context={
                'prestatario': prestatario,
                'form': form,
                'materias': prestatario.materias()
            },
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

        try:
            solicitudes_pendientes_ap = Orden.objects.filter(prestatario=prestatario, estado=Orden.Estado.PENDIENTE_AP)
            solicitudes_pendientes_ap.order_by('emision')
        except:
            solicitudes_pendientes_ap = None

        try:
            solicitudes_pendientes_cr = Orden.objects.filter(prestatario=prestatario, estado=Orden.Estado.PENDIENTE_CR)
            solicitudes_pendientes_cr.order_by('emision')
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

        context = {'solicitudes_pendientes_ap': solicitudes_pendientes_ap,
                   'solicitudes_pendientes_cr': solicitudes_pendientes_cr,
                   'solicitudes_aprobadas': solicitudes_aprobadas,
                   'solicitudes_rechazadas': solicitudes_rechazadas,
                   'solicitudes_canceladas': solicitudes_canceladas, }

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


class CatalogoView(UserPassesTestMixin, LoginRequiredMixin, View):

    def test_func(self):
        prestatario = Prestatario.get_user(self.request.user)
        return prestatario.tiene_carrito()

    def get(self, request):
        prestatario = Prestatario.get_user(request.user)
        carrito = prestatario.carrito()

        return render(
            request=request,
            template_name="catalogo.html",
            context={
                "articulos": carrito.materia.articulos(),
                "carrito": prestatario.carrito(),
                "categorias": Categoria.objects.all()
            },
        )

    def post(self, request):
        prestatario = Prestatario.get_user(request.user)
        carrito = prestatario.carrito()
        categoria = request.POST["categoria"]
        articulos = carrito.materia.articulos()

        if categoria != "todos":
            categoria_instance = get_object_or_404(Categoria, pk=request.POST["categoria"])
            articulos = articulos.filter(id__in=categoria_instance.articulos())

        return render(
            request=request,
            template_name="catalogo.html",
            context={
                "articulos": articulos,
                "carrito": prestatario.carrito(),
                "categorias": Categoria.objects.all()
            },
        )


class DetallesArticuloView(View):
    def get(self, request, id):
        articulo = get_object_or_404(Articulo, id=id)

        return render(
            request=request,
            template_name="detalles_articulo.html",
            context={"articulo": articulo},
        )


class AgregarAlCarritoView(View, UserPassesTestMixin, LoginRequiredMixin):

    def test_func(self):
        prestatario = Prestatario.get_user(self.request.user)
        return prestatario.tiene_carrito()

    def get(self, request, articulo_id):
        carrito = get_object_or_404(Carrito, prestatario=request.user)
        articulo = get_object_or_404(Articulo, id=articulo_id)

        carrito.agregar(articulo, 1)
        carrito.save()

        return redirect("catalogo")


class CancelarOrdenView(View):
    def get(self, request):
        return render(
            request=request,
            template_name="cancelar_orden.html"
        )


class ActualizarAutorizacion(LoginRequiredMixin, View):

    def get(self, request, type, state, id):

        match type:
            case "corresponsable":
                solicitud = get_object_or_404(CorresponsableOrden, pk=id)

            case _:
                raise Http404("No existe ese tipo de autorizacion")

        match state:
            case "aceptar":
                solicitud.aceptar()

            case "rechazar":
                solicitud.rechazar()

            case _:
                raise Http404("No existe ese estado")

        # regresar a la pagina de autorizaciones 
        return redirect("autorizacion_solicitudes", type, id)


class AutorizacionSolitudView(LoginRequiredMixin, View):
    TEMPLATE = "autorizacion_solicitudes.html"

    def get(self, request, type, id):
        match type:
            case "corresponsable":
                solicitud = get_object_or_404(CorresponsableOrden, pk=id)

                # si el usuario no es la presona solicitada no lo puede ver
                if solicitud.autorizador != request.user:
                    raise Http404("No tienes permiso de ver esta Orden")

                return render(
                    request=request,
                    template_name=self.TEMPLATE,
                    context={
                        "solicitud": solicitud,
                        "orden": solicitud.orden
                    }
                )

        raise Http404("No existe ese tipo de autorizacion")

######################ALMACEN###############################

#######################VISTA PRINCIPAL#########################

class PrincipalAlmacenView(LoginRequiredMixin, View):
    def get(self, request):
        ordenes_aprobadas = Orden.objects.filter(estado=EstadoOrden.APROBADA)

        print("ESTOOO",ordenes_aprobadas)  # Comprueba si obtienes resultados aquí

        return render(
            request=request,
            template_name="principal.html",
            context={"ordenes": ordenes_aprobadas}
        )


#########ORDENES AUTORIZADAS#############


class DetallesOrdenAutorizadaView(View):
    def get(self, request, id):
        orden = get_object_or_404(Orden, id=id, estado=EstadoOrden.APROBADA)

        return render(
            context = {"orden": orden}

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


#####NOOOOOOOO#############
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


