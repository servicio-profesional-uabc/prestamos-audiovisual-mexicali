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
from .models import Articulo, AutorizacionOrden, Categoria, CorresponsableOrden, Maestro, Materia
from .models import Carrito, Prestatario
from .models import Orden, EstadoOrden, Perfil


class IndexView(View):
    """
    View para la página de inicio.

    Métodos:
        get(request): Renderiza la plantilla 'index.html'.
    """

    def get(self, request):
        """
        Maneja las solicitudes GET para la página de inicio.

        Args:
            request (HttpRequest): La solicitud HTTP.

        Returns:
            HttpResponse: La respuesta HTTP con la plantilla renderizada.
        """
        return render(
            request=request,
            template_name="index.html"
        )


class AgregarCorresponsablesView(UpdateView):
    """
    View para agregar corresponsables a un carrito.

    Atributos:
        model (Model): Modelo a actualizar.
        form_class (Form): Formulario a utilizar.
        template_name (str): Nombre de la plantilla a renderizar.
        success_url (str): URL a la que redirigir en caso de éxito.
    """
    model = Carrito
    form_class = CorresponsableForm
    template_name = 'agregar_corresponsables.html'
    success_url = reverse_lazy('carrito')

    def get_object(self, queryset=None):
        """
        Obtiene el objeto Carrito del prestatario actual.

        Args:
            queryset (QuerySet, optional): Conjunto de consulta.

        Returns:
            Carrito: El objeto Carrito del prestatario.
        """
        user = self.request.user
        return get_object_or_404(Carrito, prestatario=user)

    def get_form_kwargs(self):
        """
        Obtiene los argumentos para el formulario.

        Returns:
            dict: Argumentos del formulario.
        """
        kwargs = super().get_form_kwargs()
        carrito = self.get_object()
        kwargs['instance'] = carrito
        kwargs['materia'] = carrito.materia
        return kwargs

    def form_valid(self, form):
        """
        Maneja el formulario válido.

        Args:
            form (Form): El formulario validado.

        Returns:
            HttpResponse: La respuesta HTTP.
        """
        response = super().form_valid(form)
        form.instance._corresponsables.clear()
        for corresponsable in form.cleaned_data['corresponsables']:
            form.instance._corresponsables.add(corresponsable)
        return response

    def get_success_url(self):
        """
        Obtiene la URL de éxito.

        Returns:
            str: URL de éxito.
        """
        return reverse_lazy('carrito')


class ActualizarPerfilView(LoginRequiredMixin, View):
    """
    Vista para registrar los datos faltantes del usuario.

    Métodos:
        get(request): Renderiza la plantilla para actualizar el perfil.
        post(request): Procesa el formulario de actualización del perfil.
    """

    def get(self, request):
        """
        Renderiza la plantilla para actualizar el perfil.

        Args:
            request (HttpRequest): La solicitud HTTP.

        Returns:
            HttpResponse: La respuesta HTTP con la plantilla renderizada.
        """
        return render(
            request=request,
            template_name="actualizar_perfil_y_usuario.html",
            context={
                'form_actualizar_perfil': ActualizarPerfil(),
                'form_actualizar_usuario': UpdateUserForm(),
            }
        )

    def post(self, request):
        """
        Procesa el formulario de actualización del perfil.

        Args:
            request (HttpRequest): La solicitud HTTP.

        Returns:
            HttpResponse: Redirección o respuesta con errores de formulario.
        """
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
    Vista para mostrar el menú principal del usuario.

    Métodos:
        get(request): Renderiza la plantilla del menú.
        post(request): Método POST vacío.
    """

    def get(self, request):
        """
        Renderiza la plantilla del menú.

        Args:
            request (HttpRequest): La solicitud HTTP.

        Returns:
            HttpResponse: La respuesta HTTP con la plantilla renderizada.
        """
        datos_usuario = Perfil.user_data(user=request.user)

        if datos_usuario.incompleto():
            return redirect('actualizar_perfil')

        return render(
            request=request,
            template_name="menu/menu.html",
            context={'matricula': request.user.username, 'user': request.user}
        )

    def post(self, request):
        """
        Método POST vacío.

        Args:
            request (HttpRequest): La solicitud HTTP.

        """
        pass


class CarritoView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Vista para gestionar el carrito de un prestatario.

    Métodos:
        test_func(): Verifica si el usuario tiene un carrito.
        get(request, accion=None): Maneja las solicitudes GET para el carrito.
        post(request, accion): Maneja las solicitudes POST para el carrito.
    """

    def test_func(self):
        """
        Verifica si el usuario tiene un carrito.

        Returns:
            bool: True si el usuario tiene un carrito, False en caso contrario.
        """
        prestatario = Prestatario.get_user(self.request.user)
        return prestatario.tiene_carrito()

    def get(self, request, accion=None):
        """
        Maneja las solicitudes GET para el carrito.

        Args:
            request (HttpRequest): La solicitud HTTP.
            accion (str, optional): Acción a realizar.

        Returns:
            HttpResponse: La respuesta HTTP con la plantilla renderizada.
        """
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
        """
        Maneja las solicitudes POST para el carrito.

        Args:
            request (HttpRequest): La solicitud HTTP.
            accion (str): Acción a realizar.

        Returns:
            HttpResponse: Redirección según la acción realizada.
        """
        if accion == 'ordenar':
            carrito = Prestatario.get_user(request.user).carrito()
            ordenado = carrito.ordenar()

            if ordenado:
                return redirect("historial_solicitudes")

        return redirect("carrito")


class FiltrosView(LoginRequiredMixin, View):
    """
    Vista para gestionar los filtros de búsqueda de artículos.

    Métodos:
        get(request): Renderiza la plantilla de filtros.
        post(request): Procesa el formulario de filtros.
    """

    def get(self, request):
        """
        Renderiza la plantilla de filtros.

        Args:
            request (HttpRequest): La solicitud HTTP.

        Returns:
            HttpResponse: La respuesta HTTP con la plantilla renderizada.
        """
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
        """
        Procesa el formulario de filtros.

        Args:
            request (HttpRequest): La solicitud HTTP.

        Returns:
            HttpResponse: Redirección o respuesta con errores de formulario.
        """
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
    Vista para mostrar la página de solicitud.

    Métodos:
        get(request): Renderiza la plantilla 'solicitud.html'.
    """

    def get(self, request):
        """
        Maneja las solicitudes GET para la página de solicitud.

        Args:
            request (HttpRequest): La solicitud HTTP.

        Returns:
            HttpResponse: La respuesta HTTP con la plantilla renderizada.
        """
        return render(
            request=request,
            template_name="solicitud.html"
        )


class HistorialSolicitudesView(View):
    """
    Vista para mostrar el historial de solicitudes del prestatario.

    Métodos:
        get(request): Renderiza la plantilla del historial de solicitudes.
    """

    def get(self, request):
        """
        Maneja las solicitudes GET para el historial de solicitudes.

        Args:
            request (HttpRequest): La solicitud HTTP.

        Returns:
            HttpResponse: La respuesta HTTP con la plantilla renderizada.
        """
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
    Vista para mostrar los detalles de una orden específica.

    Métodos:
        test_func(): Verifica si el usuario es el prestatario de la orden.
        get(request, id): Renderiza la plantilla de detalles de la orden.
        post(request, id): Maneja la cancelación de una orden.
    """

    def test_func(self):
        """
        Verifica si el usuario es el prestatario de la orden.

        Returns:
            bool: True si el usuario es el prestatario de la orden, False en caso contrario.
        """
        prestatario = Prestatario.get_user(self.request.user)
        orden = get_object_or_404(Orden, id=self.kwargs['id'])
        return prestatario == orden.prestatario

    def get(self, request, id):
        """
        Renderiza la plantilla de detalles de la orden.

        Args:
            request (HttpRequest): La solicitud HTTP.
            id (int): El ID de la orden.

        Returns:
            HttpResponse: La respuesta HTTP con la plantilla renderizada.
        """
        orden = Orden.objects.get(id=id)
        return render(
            request=request,
            template_name="detalles_orden.html",
            context={"orden": orden,
                     "EstadoOrden": EstadoOrden}
        )

    def post(self, request, id):
        """
        Maneja la cancelación de una orden.

        Args:
            request (HttpRequest): La solicitud HTTP.
            id (int): El ID de la orden.

        Returns:
            HttpResponse: Redirección al historial de solicitudes con un mensaje de éxito.
        """
        orden = get_object_or_404(Orden, id=id)
        orden.cancelar()
        orden.save()
        messages.success(request, "Haz cancelado tu orden exitosamente.")
        return redirect("historial_solicitudes")


class CatalogoView(View, LoginRequiredMixin, UserPassesTestMixin):
    """
    Vista donde el usuario agrega artículos a su carrito.

    Métodos:
        test_func(): Verifica si el prestatario ha comenzado el proceso de carrito.
        get(request): Renderiza la plantilla del catálogo con los artículos disponibles.
        post(request): Filtra los artículos según la categoría seleccionada.
    """

    def test_func(self):
        """
        Verifica si el prestatario ha comenzado el proceso de carrito (debió haber completado Filtro).

        Returns:
            bool: True si el prestatario ha comenzado el proceso de carrito, False en caso contrario.
        """
        prestatario = Prestatario.get_user(self.request.user)
        carrito = get_object_or_404(Carrito, prestatario=prestatario)
        return prestatario == carrito.prestatario

    def get(self, request):
        """
        Renderiza la plantilla del catálogo con los artículos disponibles.

        Args:
            request (HttpRequest): La solicitud HTTP.

        Returns:
            HttpResponse: La respuesta HTTP con la plantilla renderizada.
        """
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
        """
        Filtra los artículos según la categoría seleccionada.

        Args:
            request (HttpRequest): La solicitud HTTP.

        Returns:
            HttpResponse: La respuesta HTTP con la plantilla renderizada con los artículos filtrados.
        """
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
    Vista para mostrar los detalles de un artículo específico.

    Métodos:
        get(request, id): Renderiza la plantilla de detalles del artículo.
    """

    def get(self, request, id):
        """
        Renderiza la plantilla de detalles del artículo.

        Args:
            request (HttpRequest): La solicitud HTTP.
            id (int): El ID del artículo.

        Returns:
            HttpResponse: La respuesta HTTP con la plantilla renderizada.
        """
        articulo = get_object_or_404(Articulo, id=id)

        return render(
            request=request,
            template_name="detalles_articulo.html",
            context={"articulo": articulo},
        )


class AgregarAlCarritoView(View, UserPassesTestMixin, LoginRequiredMixin):
    """
    Vista para agregar un artículo al carrito del prestatario.

    Métodos:
        test_func(): Verifica si el prestatario tiene un carrito.
        post(request, articulo_id): Maneja la adición de un artículo al carrito.
    """

    def test_func(self):
        """
        Verifica si el prestatario tiene un carrito.

        Returns:
            bool: True si el prestatario tiene un carrito, False en caso contrario.
        """
        prestatario = Prestatario.get_user(self.request.user)
        return prestatario.tiene_carrito()

    def post(self, request, articulo_id):
        """
        Maneja la adición de un artículo al carrito.

        Args:
            request (HttpRequest): La solicitud HTTP.
            articulo_id (int): El ID del artículo a agregar.

        Returns:
            HttpResponse: Redirección al catálogo.
        """
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
    Vista para eliminar un artículo del carrito del prestatario.

    Métodos:
        test_func(): Verifica si el prestatario tiene un carrito.
        get(request, articulo_id): Maneja la eliminación de un artículo del carrito.
    """

    def test_func(self):
        """
        Verifica si el prestatario tiene un carrito.

        Returns:
            bool: True si el prestatario tiene un carrito, False en caso contrario.
        """
        prestatario = Prestatario.get_user(self.request.user)
        return prestatario.tiene_carrito()

    def get(self, request, articulo_id):
        """
        Maneja la eliminación de un artículo del carrito.

        Args:
            request (HttpRequest): La solicitud HTTP.
            articulo_id (int): El ID del artículo a eliminar.

        Returns:
            HttpResponse: Redirección al carrito.
        """
        carrito = get_object_or_404(Carrito, prestatario=request.user)
        articulo = get_object_or_404(Articulo, id=articulo_id)

        carrito.eliminar_articulo(articulo)
        carrito.save()

        return redirect("carrito")


class CancelarOrdenView(View):
    """
    Vista para mostrar la página de cancelación de orden.

    Métodos:
        get(request): Renderiza la plantilla 'cancelar_orden.html'.
    """

    def get(self, request):
        """
        Maneja las solicitudes GET para la página de cancelación de orden.

        Args:
            request (HttpRequest): La solicitud HTTP.

        Returns:
            HttpResponse: La respuesta HTTP con la plantilla renderizada.
        """
        return render(
            request=request,
            template_name="cancelar_orden.html"
        )
class ActualizarAutorizacion(LoginRequiredMixin, View):
    """
    Vista para actualizar la autorización de una orden por parte de un corresponsable o aprobador.

    Métodos:
        get(request, type, state, id): Maneja la aceptación o rechazo de una orden.
    """

    def get(self, request, type, state, id):
        """
        Corresponsable puede aceptar o rechazar una orden de otro prestatario.
        Aprobador es Maestro o Coordinador quien puede aprobar o cancelar la orden de un prestatario o propia en caso de ser Maestro.

        Args:
            request (HttpRequest): La solicitud HTTP.
            type (str): El tipo de autorización ('corresponsable' o 'aprobacion').
            state (str): El estado de la autorización ('aceptar', 'rechazar', 'aprobar' o 'rechazar').
            id (int): El ID de la solicitud de autorización.

        Returns:
            HttpResponse: Redirección a la página de autorizaciones.
        """
        match type:
            case "corresponsable":
                solicitud = get_object_or_404(CorresponsableOrden, pk=id)

            case "aprobacion":
                solicitud = get_object_or_404(AutorizacionOrden, orden_id=id)

            case _:
                raise Http404("No existe ese tipo de autorización")

        if type == "corresponsable":
            match state:
                case "aceptar":
                    solicitud.aceptar()

                case "rechazar":
                    solicitud.rechazar()

                case _:
                    raise Http404("No existe ese estado")
        else:
            match state:
                case "aprobar":
                    solicitud.orden.aprobar()
                    solicitud.orden.save()

                case "rechazar":
                    solicitud.orden.cancelar()
                    solicitud.orden.save()

                case _:
                    raise Http404("No existe ese estado")

        return redirect("autorizacion_solicitudes", type, id)


class AutorizacionSolicitudView(LoginRequiredMixin, View):
    """
    Vista para mostrar las solicitudes de autorización.

    Métodos:
        get(request, type, id): Renderiza la plantilla correspondiente según el tipo de solicitud.
    """
    autorizacion_template = "autorizacion_solicitudes.html"
    aprobacion_template = "aprobacion_solicitudes.html"

    def get(self, request, type, id):
        """
        Renderiza la plantilla correspondiente según el tipo de solicitud.

        Args:
            request (HttpRequest): La solicitud HTTP.
            type (str): El tipo de autorización ('corresponsable' o 'aprobacion').
            id (int): El ID de la solicitud de autorización.

        Returns:
            HttpResponse: La respuesta HTTP con la plantilla renderizada.
        """
        match type:
            case "corresponsable":
                solicitud = get_object_or_404(CorresponsableOrden, pk=id)

                if solicitud.autorizador != request.user:
                    raise Http404("No tienes permiso de ver esta Orden")

                return render(
                    request=request,
                    template_name=self.autorizacion_template,
                    context={
                        "solicitud": solicitud,
                        "orden": solicitud.orden
                    }
                )

            case "aprobacion":
                solicitud = get_object_or_404(AutorizacionOrden, orden_id=id)

                if solicitud.autorizador != request.user:
                    raise Http404("No tienes permiso de ver esta Orden")

                return render(
                    request=request,
                    template_name=self.aprobacion_template,
                    context={
                        "solicitud": solicitud,
                        "orden": solicitud.orden
                    }
                )

        raise Http404("No existe ese tipo de autorización")


class DetallesOrdenAutorizadaView(View):
    """
    Vista para mostrar los detalles de una orden aprobada.

    Métodos:
        get(request, id): Renderiza la plantilla de detalles de la orden aprobada.
    """

    def get(self, request, id):
        """
        Renderiza la plantilla de detalles de la orden aprobada.

        Args:
            request (HttpRequest): La solicitud HTTP.
            id (int): El ID de la orden aprobada.

        Returns:
            HttpResponse: La respuesta HTTP con la plantilla renderizada.
        """
        orden = get_object_or_404(Orden, id=id, estado=EstadoOrden.APROBADA)

        return render(
            request=request,
            template_name="detalles_orden_autorizada.html",
            context={"orden": orden}
        )


class OrdenesPrestadasView(View):
    """
    Vista para mostrar las órdenes prestadas.

    Métodos:
        get(request): Renderiza la plantilla con la lista de órdenes prestadas.
    """

    def get(self, request):
        """
        Renderiza la plantilla con la lista de órdenes prestadas.

        Args:
            request (HttpRequest): La solicitud HTTP.

        Returns:
            HttpResponse: La respuesta HTTP con la plantilla renderizada.
        """
        ordenes_prestadas = Orden.objects.filter(estado=EstadoOrden.ENTREGADA)
        print("ESTOOO 2", ordenes_prestadas)

        return render(
            request=request,
            template_name="almacen_permisos/ordenes_prestadas.html",
            context={'ordenes': ordenes_prestadas}
        )


class DetallesOrdenPrestadaView(View):
    """
    Vista para mostrar los detalles de una orden prestada.

    Métodos:
        get(request, id): Renderiza la plantilla de detalles de la orden prestada.
    """

    def get(self, request, id):
        """
        Renderiza la plantilla de detalles de la orden prestada.

        Args:
            request (HttpRequest): La solicitud HTTP.
            id (int): El ID de la orden prestada.

        Returns:
            HttpResponse: La respuesta HTTP con la plantilla renderizada.
        """
        orden = get_object_or_404(Orden, id=id, estado=EstadoOrden.ENTREGADA)

        return render(
            request=request,
            template_name="detalles_orden_prestada.html",
            context={"orden": orden}
        )


class OrdenesReportadasView(View):
    """
    Vista para mostrar las órdenes reportadas.

    Métodos:
        get(request): Renderiza la plantilla con la lista de órdenes reportadas.
    """

    def get(self, request):
        """
        Renderiza la plantilla con la lista de órdenes reportadas.

        Args:
            request (HttpRequest): La solicitud HTTP.

        Returns:
            HttpResponse: La respuesta HTTP con la plantilla renderizada.
        """
        ordenes_devueltas = Orden.objects.filter(estado=EstadoOrden.RECHAZADA)

        return render(
            request=request,
            template_name="almacen_permisos/ordenes_reportadas.html",
            context={'ordenes': ordenes_devueltas}
        )


class ReportarOrdenView(View):
    """
    Vista para reportar una orden.

    Métodos:
        get(request, id): Renderiza la plantilla para reportar una orden.
    """

    def get(self, request, id):
        """
        Renderiza la plantilla para reportar una orden.

        Args:
            request (HttpRequest): La solicitud HTTP.
            id (int): El ID de la orden a reportar.

        Returns:
            HttpResponse: La respuesta HTTP con la plantilla renderizada.
        """
        return render(
            request=request,
            template_name="reportar_orden.html"
        )


class DetallesOrdenReportadaView(View):
    """
    Vista para mostrar los detalles de una orden reportada.

    Métodos:
        get(request, id): Renderiza la plantilla de detalles de la orden reportada.
    """

    def get(self, request, id):
        """
        Renderiza la plantilla de detalles de la orden reportada.

        Args:
            request (HttpRequest): La solicitud HTTP.
            id (int): El ID de la orden reportada.

        Returns:
            HttpResponse: La respuesta HTTP con la plantilla renderizada.
        """
        orden = get_object_or_404(Orden, id=id, estado=EstadoOrden.RECHAZADA)

        return render(
            request=request,
            template_name="almacen_permisos/detalles_orden_reportada.html",
            context={"orden": orden}
        )


class OrdenesDevueltasView(View):
    """
    Vista para mostrar las órdenes devueltas.

    Métodos:
        get(request): Renderiza la plantilla con la lista de órdenes devueltas.
    """

    def get(self, request):
        """
        Renderiza la plantilla con la lista de órdenes devueltas.

        Args:
            request (HttpRequest): La solicitud HTTP.

        Returns:
            HttpResponse: La respuesta HTTP con la plantilla renderizada.
        """
        ordenes_devueltas = Orden.objects.filter(estado=EstadoOrden.DEVUELTA)
        print("EST 33", ordenes_devueltas)

        return render(
            request=request,
            template_name="almacen_permisos/ordenes_devueltas.html",
            context={'ordenes': ordenes_devueltas}
        )


class DetallesOrdenDevueltaView(View):
    """
    Vista para mostrar los detalles de una orden devuelta.

    Métodos:
        get(request, id): Renderiza la plantilla de detalles de la orden devuelta.
    """

    def get(self, request, id):
        """
        Renderiza la plantilla de detalles de la orden devuelta.

        Args:
            request (HttpRequest): La solicitud HTTP.
            id (int): El ID de la orden devuelta.

        Returns:
            HttpResponse: La respuesta HTTP con la plantilla renderizada.
        """
        orden = get_object_or_404(Orden, id=id, estado=EstadoOrden.DEVUELTA)

        return render(
            request=request,
            template_name="almacen_permisos/detalles_orden_devuelta.html",
            context={"orden": orden}
        )


class OrdenesReportadasCordinadorView(View):
    """
    Vista para mostrar las órdenes reportadas al coordinador.

    Métodos:
        get(request): Renderiza la plantilla con la lista de órdenes reportadas.
    """

    def get(self, request):
        """
        Renderiza la plantilla con la lista de órdenes reportadas al coordinador.

        Args:
            request (HttpRequest): La solicitud HTTP.

        Returns:
            HttpResponse: La respuesta HTTP con la plantilla renderizada.
        """
        return render(
            request=request,
            template_name="coordinador_permisos/ordenes_reportadas_cordi.html"
        )


def cambiar_estado_ENTREGADO(request, orden_id, estado):
    """
    Cambia el estado de una orden a 'ENTREGADA'.

    Args:
        request (HttpRequest): La solicitud HTTP.
        orden_id (int): El ID de la orden.
        estado (str): El nuevo estado de la orden.

    Returns:
        HttpResponse: Redirección a la página de órdenes prestadas.
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
    Cambia el estado de una orden a 'DEVUELTA'.

    Args:
        request (HttpRequest): La solicitud HTTP.
        orden_id (int): El ID de la orden.
        estado (str): El nuevo estado de la orden.

    Returns:
        HttpResponse: Redirección a la página de órdenes devueltas.
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
    Vista para mostrar las órdenes según su estado.

    Args:
        request (HttpRequest): La solicitud HTTP.
        tipo_estado (str): El tipo de estado de las órdenes a mostrar.

    Returns:
        HttpResponse: La respuesta HTTP con la plantilla renderizada.
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
