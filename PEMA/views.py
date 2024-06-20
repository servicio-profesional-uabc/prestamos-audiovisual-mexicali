from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.timezone import make_aware
from django.views import View
from django.views.generic.edit import UpdateView

from .forms import CorresponsableForm
from .forms import FiltrosForm, ActualizarPerfil, UpdateUserForm
from .models import Articulo, Categoria, CorresponsableOrden, Maestro, Materia
from .models import Carrito, Prestatario
from .models import Orden, EstadoOrden, Perfil


class IndexView(View):
    """
    Mostrar la página de inicio.

    Renderiza la plantilla index.html al recibir una solicitud GET.
    """

    def get(self, request):
        return render(
            request=request,
            template_name="index.html"
        )


class AgregarCorresponsablesView(UpdateView):
    """
    Agregar corresponsables a un carrito.

    Renderiza la plantilla agregar_corresponsables.html, obtiene el
    carrito del usuario y actualiza los corresponsables seleccionados.
    """
    model = Carrito
    form_class = CorresponsableForm
    template_name = 'agregar_corresponsables.html'
    success_url = reverse_lazy('carrito')

    def get_object(self, queryset=None):
        user = self.request.user
        return get_object_or_404(Carrito, prestatario=user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        carrito = self.get_object()
        kwargs['instance'] = carrito
        kwargs['materia'] = carrito.materia
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        form.instance._corresponsables.clear()
        for corresponsable in form.cleaned_data['corresponsables']:
            form.instance._corresponsables.add(corresponsable)
        return response

    def get_success_url(self):
        return reverse_lazy('carrito')


class ActualizarPerfilView(LoginRequiredMixin, View):
    """
    Completar y actualizar datos faltantes del usuario.

    Muestra formularios para actualizar el perfil y los datos de usuario en
    actualizar_perfil_y_usuario.html. Procesa y guarda los cambios al enviar los formularios.

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
    """
    Muestra  el menú principal del usuario.

    Verifica si el perfil del usuario está completo.
    Si no lo está, redirige a la vista de actualización de perfil, caso contrario, si está completo,
    muestra la plantilla menu/menu.html con información del usuario.
    """

    def get(self, request):
        datos_usuario = Perfil.user_data(user=request.user)

        if datos_usuario.incompleto():
            return redirect('actualizar_perfil')

        return render(
            request=request,
            template_name="menu/menu.html",
            context={'matricula': request.user.username, 'user': request.user}
        )

    def post(self, request):
        pass


class CarritoView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Gestionar el carrito de un prestatario.

    Verifica si el usuario tiene un carrito.
    Obtiene y muestra los artículos en el carrito, notificando si alguno no está disponible.
    Maneja acciones específicas como ordenar el carrito y redirige según la acción realizada.
    """

    def test_func(self):
        prestatario = Prestatario.get_user(self.request.user)
        return prestatario.tiene_carrito()

    def get(self, request, accion=None):

        prestatario = Prestatario.get_user(request.user)
        carrito = prestatario.carrito()
        articulos_no_disponibles = []

        for articulo_carrito in carrito.articulos_carrito():
            if not articulo_carrito.articulo.disponible(carrito.inicio, carrito.final).exists():
                articulos_no_disponibles.append(articulo_carrito)
                messages.add_message(request, messages.WARNING, f'El artículo {articulo_carrito.articulo.nombre} no está disponible.')

        return render(
            request=request,
            template_name="carrito.html",
            context={
                "articulos_carrito": carrito.articulos_carrito(),
                "carrito": carrito,
                "numero_unidades": carrito.numero_unidades()
            }
        )

    def post(self, request, accion):
        if accion == 'ordenar':
            carrito = Prestatario.get_user(request.user).carrito()
            ordenado = carrito.ordenar()

            if ordenado:
                return redirect("historial_solicitudes")

        return redirect("carrito")


class FiltrosView(LoginRequiredMixin, View):
    """
    Gestionar los filtros de búsqueda de artículos.

    Renderiza la plantilla de filtros y elimina el carrito existente del prestatario si lo tiene.
    Procesa el formulario de filtros, crea y guarda un nuevo carrito con los datos proporcionados,
    y redirige al catálogo si el formulario es válido.
    """

    def get(self, request):
        prestatario = Prestatario.get_user(request.user)

        if prestatario.tiene_carrito():
            prestatario.carrito().eliminar()

        for materia in prestatario.materias():
            if materia.son_correos_vacios():
                messages.add_message(request, messages.WARNING, f'La materia {materia.nombre} no está disponible porque no hay maestro con sus datos registrados como es su correo electrónico y/o número de celular. Por favor contacta al maestro para que actualice sus datos.')

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
            prestatario.carrito().eliminar()

        if form.is_valid():
            inicio = form.cleaned_data.get('inicio')
            hora_inicio = form.cleaned_data.get('hora_inicio')
            duracion = form.cleaned_data.get('duracion')

            carrito_nuevo = form.save(commit=False)
            carrito_nuevo.prestatario = request.user

            tiempo_duracion = int(duracion)
            fecha_inicio = datetime.combine(inicio, hora_inicio)

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
                'materias': prestatario.materias(),
            },
        )
class SolicitudView(View):
    """
    Mostrar la página de solicitud.

    Renderiza la plantilla solicitud.html.
    """

    def get(self, request):
        return render(
            request=request,
            template_name="solicitud.html"
        )


class HistorialSolicitudesView(View):
    """
    Mostrar el historial de solicitudes del prestatario.

    Obtiene y muestra las solicitudes del prestatario clasificadas en pendientes,
    listas para entregar, canceladas, entregadas y devueltas.
    """

    def get(self, request):

        prestatario = Prestatario.get_user(request.user)

        ordenes_pendientes = Orden.objects.filter(prestatario=prestatario, estado=EstadoOrden.RESERVADA)
        ordenes_listas = Orden.objects.filter(prestatario=prestatario, estado=EstadoOrden.APROBADA)
        ordenes_canceladas = Orden.objects.filter(prestatario=prestatario, estado=EstadoOrden.CANCELADA)
        ordenes_entregadas = Orden.objects.filter(prestatario=prestatario, estado=EstadoOrden.ENTREGADA)
        ordenes_devueltas = Orden.objects.filter(prestatario=prestatario, estado=EstadoOrden.DEVUELTA)

        context = {
            "ordenes_pendientes": ordenes_pendientes,
            "ordenes_listas": ordenes_listas,
            "ordenes_canceladas": ordenes_canceladas,
            "ordenes_entregadas": ordenes_entregadas,
            "ordenes_devueltas": ordenes_devueltas,
        }

        return render(
            request=request,
            template_name="historial_solicitudes.html",
            context=context,
        )


class DetallesOrdenView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Mostrar los detalles de una orden específica.


    Primero verifica si el usuario es el prestatario de la orden.
    Muestra los detalles de la orden.
    Maneja la cancelación de una orden y guarda el cambio.
    """

    def test_func(self):
        prestatario = Prestatario.get_user(self.request.user)
        orden = get_object_or_404(Orden, id=self.kwargs['id'])
        return prestatario == orden.prestatario

    def get(self, request, id):
        orden = Orden.objects.get(id=id)
        return render(
            request=request,
            template_name="detalles_orden.html",
            context={"orden": orden,
                     "EstadoOrden": EstadoOrden}
        )

    def post(self, request, id):
        orden = get_object_or_404(Orden, id=id)
        orden.cancelar()
        orden.save()
        messages.success(request, "Haz cancelado tu orden exitosamente.")
        return redirect("historial_solicitudes")


class CatalogoView(View, LoginRequiredMixin, UserPassesTestMixin):
    """
    Permitir al usuario agregar artículos a su carrito.

    Verifica si el prestatario ha comenzado el proceso de carrito.
    Muestra los artículos disponibles en el catálogo.
    Filtra los artículos según la categoría seleccionada.
    """

    def test_func(self):
        prestatario = Prestatario.get_user(self.request.user)
        carrito = get_object_or_404(Carrito, prestatario=prestatario)
        return prestatario == carrito.prestatario

    def get(self, request):
        prestatario = Prestatario.get_user(request.user)
        carrito = prestatario.carrito()

        # Filtrar las unidades disponibles para cada artículo
        articulos_disponibles = []
        for articulo in carrito.materia.articulos():
            cantidad_disponible = articulo.disponible(carrito.inicio, carrito.final).count()
            if cantidad_disponible > 0:
                articulos_disponibles.append(articulo)
                articulo.num_unidades = cantidad_disponible
            else:
                articulo.num_unidades = 0

        return render(
            request=request,
            template_name="catalogo.html",
            context={
                "articulos": articulos_disponibles,
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
    """
    Mostrar los detalles de un artículo específico.

    Muestra los detalles de un artículo.
    """

    def get(self, request, id):
        articulo = get_object_or_404(Articulo, id=id)

        return render(
            request=request,
            template_name="detalles_articulo.html",
            context={"articulo": articulo},
        )


class AgregarAlCarritoView(View, UserPassesTestMixin, LoginRequiredMixin):
    """
    Agregar un artículo al carrito del prestatario.

    Verifica si el prestatario tiene un carrito.
    Añade un artículo al carrito y guarda los cambios.

    """

    def test_func(self):
        prestatario = Prestatario.get_user(self.request.user)
        return prestatario.tiene_carrito()

    def post(self, request, articulo_id):
        carrito = get_object_or_404(Carrito, prestatario=request.user)
        articulo = get_object_or_404(Articulo, id=articulo_id)
        cantidad = int(request.POST.get('cantidad', 1))

        if carrito.existe(articulo):
            carrito.eliminar_articulo(articulo)
        carrito.agregar(articulo, cantidad)
        carrito.save()

        return redirect("catalogo")


class EliminarDelCarritoView(View, UserPassesTestMixin, LoginRequiredMixin):
    """
    Eliminar un artículo del carrito del prestatario.

    Verifica si el prestatario tiene un carrito.
    Elimina un artículo del carrito y guarda los cambios.
    """

    def test_func(self):
        prestatario = Prestatario.get_user(self.request.user)
        return prestatario.tiene_carrito()

    def get(self, request, articulo_id):
        carrito = get_object_or_404(Carrito, prestatario=request.user)
        articulo = get_object_or_404(Articulo, id=articulo_id)

        carrito.eliminar_articulo(articulo)
        carrito.save()

        return redirect("carrito")


class CancelarOrdenView(View):
    """
    Muestra la página de cancelación de orden.

    Renderiza la plantilla para la cancelación de una orden.
    """

    def get(self, request):
        return render(
            request=request,
            template_name="cancelar_orden.html"
        )

class AutorizacionSolicitudView(LoginRequiredMixin, View):
    """
    Muestra las solicitudes de autorización.

    Muestra y maneja las acciones de aceptación o rechazo de una solicitud de autorización,
    verificando los permisos del usuario.
    """
    def get(self, request, id, action=None):
        solicitud = get_object_or_404(CorresponsableOrden, pk=id)

        if action == "aceptar":
            solicitud.aceptar()

        if action == "rechazar":
            solicitud.rechazar()

        if solicitud.autorizador != request.user:
            raise Http404("No tienes permiso de ver esta Orden")

        return render(
            request=request,
            template_name="autorizacion_solicitudes.html",
            context={
                "solicitud": solicitud,
                "orden": solicitud.orden
            }
        )


class DetallesOrdenAutorizadaView(View):
    """
    Muestra los detalles de una orden  que ha sido aprobada.
    """

    def get(self, request, id):
        orden = get_object_or_404(Orden, id=id, estado=EstadoOrden.APROBADA)

        return render(
            request=request,
            template_name="detalles_orden_autorizada.html",
            context={"orden": orden}
        )


class OrdenesPrestadasView(View):
    """
    Muetsra las órdenes que han sido prestadas.

    Renderiza la plantilla con la lista de órdenes que están en estado "ENTREGADA".
    """

    def get(self, request):

        ordenes_prestadas = Orden.objects.filter(estado=EstadoOrden.ENTREGADA)

        return render(
            request=request,
            template_name="almacen_permisos/ordenes_prestadas.html",
            context={'ordenes': ordenes_prestadas}
        )


class DetallesOrdenPrestadaView(View):
    """
    Muestra los detalles de una orden que ha sido prestada.

    Renderiza la plantilla con los detalles de una orden específica que está en estado "ENTREGADA".

    """

    def get(self, request, id):
        orden = get_object_or_404(Orden, id=id, estado=EstadoOrden.ENTREGADA)

        return render(
            request=request,
            template_name="detalles_orden_prestada.html",
            context={"orden": orden}
        )


class OrdenesReportadasView(View):
    """
    Mostrar las órdenes que han sido reportadas.

    Renderiza la plantilla con la lista de órdenes que están en estado "RECHAZADA".
"""

    def get(self, request):
        ordenes_devueltas = Orden.objects.filter(estado=EstadoOrden.RECHAZADA)

        return render(
            request=request,
            template_name="almacen_permisos/ordenes_reportadas.html",
            context={'ordenes': ordenes_devueltas}
        )


class ReportarOrdenView(View):
    """
    Permitir al usuario regirigirse a una seccion para reportar una orden.

    Renderiza la plantilla para reportar una orden específica.
    """

    def get(self, request, id):
        return render(
            request=request,
            template_name="reportar_orden.html"
        )


class DetallesOrdenReportadaView(View):
    """
    Muetsra los detalles de una orden que ha sido reportada.

    Renderiza la plantilla con los detalles de una orden específica que está en estado "RECHAZADA".

    """

    def get(self, request, id):
        orden = get_object_or_404(Orden, id=id, estado=EstadoOrden.RECHAZADA)

        return render(
            request=request,
            template_name="almacen_permisos/detalles_orden_reportada.html",
            context={"orden": orden}
        )


class OrdenesDevueltasView(View):
    """
    Muestra las órdenes que han sido devueltas.

    Renderiza la plantilla con la lista de órdenes que están en estado "DEVUELTA".
    """

    def get(self, request):
        ordenes_devueltas = Orden.objects.filter(estado=EstadoOrden.DEVUELTA)
        print("EST 33", ordenes_devueltas)

        return render(
            request=request,
            template_name="almacen_permisos/ordenes_devueltas.html",
            context={'ordenes': ordenes_devueltas}
        )


class DetallesOrdenDevueltaView(View):
    """
    Mostrar los detalles de una orden que ha sido devuelta.

    Renderiza la plantilla con los detalles de una orden específica que está en estado "DEVUELTA".
    """

    def get(self, request, id):
        orden = get_object_or_404(Orden, id=id, estado=EstadoOrden.DEVUELTA)

        return render(
            request=request,
            template_name="almacen_permisos/detalles_orden_devuelta.html",
            context={"orden": orden}
        )


class OrdenesReportadasCordinadorView(View):
    """
    Mostrar las órdenes que han sido reportadas al coordinador.

    Renderiza la plantilla con la lista de órdenes reportadas al coordinador.
    """

    def get(self, request):
        return render(
            request=request,
            template_name="coordinador_permisos/ordenes_reportadas_cordi.html"
        )


def cambiar_estado_ENTREGADO(request, orden_id, estado):
    """
    Funcion que cambia el estado de una orden a "ENTREGADA".

    Cambia el estado de una orden específica a "ENTREGADA" y redirige a la página de órdenes prestadas.
    Maneja errores si la orden no existe o si se utiliza un método HTTP no permitido.
    """
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
    """
    Funcion para cambiar el estado de una orden a "DEVUELTA".

    Cambia el estado de una orden específica a "DEVUELTA" y redirige a la página de órdenes devueltas.
    """
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


def estado_orden(request, tipo_estado):
    """
    Funcion para mostrar las órdenes según su estado.

    Renderiza la plantilla principal con la lista de órdenes clasificadas por su
    estado: pendientes, listas, canceladas, entregadas y devueltas.
    """
    ordenes_pendientes = Orden.objects.filter(estado="Pendiente")
    ordenes_listas = Orden.objects.filter(estado="Listo para iniciar")
    ordenes_canceladas = Orden.objects.filter(estado="Cancelada")
    ordenes_entregadas = Orden.objects.filter(estado="Entregada")
    ordenes_devueltas = Orden.objects.filter(estado="Devuelta")

    context = {
        "ordenes_pendientes": ordenes_pendientes,
        "ordenes_listas": ordenes_listas,
        "ordenes_canceladas": ordenes_canceladas,
        "ordenes_entregadas": ordenes_entregadas,
        "ordenes_devueltas": ordenes_devueltas,
    }

    return render(request, "principal.html", context)
