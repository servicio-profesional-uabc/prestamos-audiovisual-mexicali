from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.timezone import make_aware
from django.views import View
from django.views.generic.edit import UpdateView
from django.contrib.auth import update_session_auth_hash
from .forms import CorresponsableForm, CambiarEstadoOrdenForm, CambiarEstadoCorresponsableOrdenForm,CambiarContrasenaForm
from .forms import FiltrosForm, ActualizarPerfil, UpdateUserForm
from .models import Articulo, Categoria, CorresponsableOrden, Coordinador, Maestro, Ubicacion
from .models import Carrito, Prestatario
from .models import Orden, EstadoOrden, Perfil


class IndexView(View):

    def get(self, request):
        return render(
            request=request,
            template_name="index.html"
        )


class AgregarCorresponsablesView(UpdateView):
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

    def get(self, request):
        perfil = Perfil.user_data(user=request.user)
        cambiar_contrasena_form = CambiarContrasenaForm(user=request.user)

        return render(
            request=request,
            template_name="actualizar_perfil_y_usuario.html",
            context={
                'form_actualizar_perfil': ActualizarPerfil(instance=perfil),
                'form_actualizar_usuario': UpdateUserForm(instance=request.user),
                'cambiar_contrasena_form': cambiar_contrasena_form
            }
        )

    def post(self, request):
        perfil = Perfil.user_data(user=request.user)
        perfil_form = ActualizarPerfil(request.POST, instance=perfil)
        usuario = UpdateUserForm(request.POST, instance=request.user)
        cambiar_contrasena_form = CambiarContrasenaForm(request.user, request.POST)

        if perfil_form.is_valid() and usuario.is_valid() and cambiar_contrasena_form.is_valid():
            perfil_form.save()
            usuario.save()
            user = cambiar_contrasena_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Perfil actualizado y contraseña cambiada con éxito.")
            return redirect('menu')

        return render(
            request=request,
            template_name="actualizar_perfil_y_usuario.html",
            context={
                'form_actualizar_perfil': perfil_form,
                'form_actualizar_usuario': usuario,
                'cambiar_contrasena_form': cambiar_contrasena_form
            }
        )


class MenuView(View, LoginRequiredMixin):

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

    def test_func(self):

        prestatario = Prestatario.get_user(self.request.user)
        return prestatario.tiene_carrito()

    def get(self, request, accion=None):
        prestatario = Prestatario.get_user(request.user)
        carrito = prestatario.carrito()
        articulos_no_disponibles = []

        if accion == 'ordenar':
            carrito = Prestatario.get_user(request.user).carrito()
            ordenado = carrito.ordenar()

            if ordenado:
                return redirect("historial_solicitudes")

        for articulo_carrito in carrito.articulos_carrito():
            if not articulo_carrito.articulo.disponible(carrito.inicio, carrito.final).exists():
                articulos_no_disponibles.append(articulo_carrito)
                messages.add_message(request, messages.WARNING,
                                     f'El artículo {articulo_carrito.articulo.nombre} no está disponible.')

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
        pass


class FiltrosView(LoginRequiredMixin, View):

    def get(self, request):
        prestatario = Prestatario.get_user(request.user)
        materias = prestatario.materias()

        coordinador = Coordinador.objects.first()
        # En caso que no exista ninguno registrado
        if coordinador is None:
            messages.add_message(request, messages.WARNING,
                                 "Órdenes extraordinarias pendientes por actualización de información del coordinador. Le recomendamos contactarlo para proceder.")

        # En caso que falta registrar sus datos
        else:
            perfil = Perfil.objects.get(usuario=coordinador)
            if perfil.incompleto():
                messages.add_message(request, messages.WARNING,
                                     "Órdenes extraordinarias pendientes por actualización de información del coordinador. Le recomendamos contactarlo para proceder.")

        if prestatario.tiene_carrito():
            prestatario.carrito().eliminar()

        for materia in prestatario.materias():
            if materia.son_correos_vacios():
                messages.add_message(request, messages.WARNING,
                                     f'La materia {materia.nombre} no está disponible porque no hay maestro con sus datos registrados como es su correo electrónico y/o número de celular. Por favor contacta al maestro para que actualice sus datos.')
        
        if request.user.groups.filter(name='maestro'):
            maestro = Maestro.get_user(request.user)
            materias = maestro.materias()

        return render(
            request=request,
            template_name="filtros.html",
            context={
                'prestatario': prestatario,
                'form': FiltrosForm(),
                'materias': materias,
            },
        )

    def post(self, request):
        prestatario = Prestatario.get_user(request.user)
        materias = prestatario.materias()

        form = FiltrosForm(request.POST)

        if prestatario.tiene_carrito():
            prestatario.carrito().eliminar()

        if request.user.groups.filter(name='maestro'):
            maestro = Maestro.get_user(request.user)
            materias = maestro.materias()

        if form.is_valid():
            inicio = form.cleaned_data.get('inicio')
            hora_inicio = form.cleaned_data.get('hora_inicio')
            duracion = int(form.cleaned_data.get('duracion'))
            lugar = form.cleaned_data.get('lugar')

            # HORARIO DE ORDENES EXTRAORDINARIAS
            if duracion in [24, 48, 72, 96] or lugar == Ubicacion.EXTERNO:
                messages.error(request, "Órdenes extraordinarias no permitidas actualmente. Contacte al coordinador.")
                return render(request, "filtros.html", {
                    'prestatario': prestatario,
                    'form': form,
                    'materias': materias,
                })

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
                'materias': materias,
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
        ordenes = prestatario.ordenes()

        return render(
            request=request,
            template_name="historial_solicitudes.html",
            context={
                "ordenes_pendientes": ordenes.filter(estado=EstadoOrden.RESERVADA),
                "ordenes_listas": ordenes.filter(estado=EstadoOrden.APROBADA),
                "ordenes_canceladas": ordenes.filter(estado=EstadoOrden.CANCELADA),
                "ordenes_entregadas": ordenes.filter(estado=EstadoOrden.ENTREGADA),
                "ordenes_devueltas": ordenes.filter(estado=EstadoOrden.DEVUELTA),
            }
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
            context={
                "orden": orden,
                "EstadoOrden": EstadoOrden
            }
        )

    def post(self, request, id):
        orden = get_object_or_404(Orden, id=id)
        orden.cancelar()
        orden.save()
        messages.success(request, "Haz cancelado tu orden exitosamente.")
        return redirect("historial_solicitudes")


class CatalogoView(View, LoginRequiredMixin, UserPassesTestMixin):

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

        # Filtrar las unidades disponibles para cada artículo
        articulos_disponibles = []
        for articulo in articulos:
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


class DetallesArticuloView(View):

    def get(self, request, id):
        prestatario = Prestatario.get_user(request.user)
        carrito = prestatario.carrito()
        articulo = get_object_or_404(Articulo, id=id)

        articulo.num_unidades = articulo.disponible(carrito.inicio, carrito.final).count()

        return render(
            request=request,
            template_name="detalles_articulo.html",
            context={"articulo": articulo},
        )


class AgregarAlCarritoView(View, UserPassesTestMixin, LoginRequiredMixin):

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


class AutorizacionSolicitudView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        orden = get_object_or_404(Orden, id=self.kwargs['id'])
        solicitud = get_object_or_404(CorresponsableOrden, orden=orden, autorizador=self.request.user)
        return solicitud.esta_pendiente() and self.request.user in orden.corresponsables()

    def get(self, request, id):
        orden = get_object_or_404(Orden, id=id)
        form = CambiarEstadoCorresponsableOrdenForm(instance=orden)
        return render(
            request=request,
            template_name='autorizar_ordenes/cambiar_estado_orden.html',
            context={
                'form': form,
                'orden': orden
            }
        )

    def post(self, request, id):
        orden = get_object_or_404(Orden, id=id)
        solicitud = get_object_or_404(CorresponsableOrden, orden=orden, autorizador=self.request.user)
        action = request.POST.get('action')

        if action == 'aprobar':
            solicitud.aceptar()

        elif action == 'cancelar':
            solicitud.rechazar()

        # TODO: mostrar mensaje si se aprobó o se canceló
        return redirect('autorizacion_solicitudes', id=id)


class CambiarEstadoOrdenView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        orden = get_object_or_404(Orden, id=self.kwargs['id'])
        materia = orden.materia
        if orden.es_extraordinaria():
            return self.request.user.groups.filter(name='coordinador').exists()
        elif orden.es_ordinaria():
            return self.request.user in materia._maestros.all()
        return False

    def get(self, request, id):
        orden = get_object_or_404(Orden, id=id, estado=EstadoOrden.RESERVADA)
        form = CambiarEstadoOrdenForm(instance=orden)
        return render(request, 'autorizar_ordenes/cambiar_estado_orden.html', {'form': form, 'orden': orden})

    def post(self, request, id):
        orden = get_object_or_404(Orden, id=id, estado=EstadoOrden.RESERVADA)
        action = request.POST.get('action')

        if action == 'aprobar':
            orden.aprobar()
        elif action == 'cancelar':
            orden.cancelar()

        # TODO: mostrar mensaje si se aprobó o se canceló
        return redirect('cambiar_estado_orden', id=id)


class EliminarDelCarritoView(View, UserPassesTestMixin, LoginRequiredMixin):

    def test_func(self):
        prestatario = Prestatario.get_user(self.request.user)
        return prestatario.tiene_carrito()

    def get(self, request, articulo_id):
        carrito = get_object_or_404(Carrito, prestatario=request.user)
        articulo = get_object_or_404(Articulo, id=articulo_id)

        carrito.eliminar_articulo(articulo)
        carrito.save()

        return redirect("carrito")
