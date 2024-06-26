from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from .forms import UserLoginForm
from .views import AgregarAlCarritoView
from .views import AgregarCorresponsablesView
from .views import AutorizacionSolicitudView
from .views import CambiarEstadoOrdenView
from .views import CarritoView
from .views import CatalogoView
from .views import DetallesArticuloView
from .views import DetallesOrdenView
from .views import EliminarDelCarritoView
from .views import FiltrosView
from .views import HistorialSolicitudesView
from .views import MenuView, ActualizarPerfilView
from .views import SolicitudView
from django.shortcuts import render

def custom_403(request, exception):
    return render(request, '403', status=403)

def custom_404(request, exception):
    return render(request, '404', status=404)


urlpatterns = [
    path(
        route='',
        name='index',
        view=LoginView.as_view(
            template_name='login.html',
            authentication_form=UserLoginForm
        )
    ),

    # login
    path(
        route='login/',
        name='login',
        view=LoginView.as_view(
            template_name='login.html',
            authentication_form=UserLoginForm
        )
    ),

    # logout
    path(
        route='logout/',
        view=LogoutView.as_view(),
        name='logout'
    ),

    path(
        route='menu',
        view=MenuView.as_view(),
        name='menu'
    ),

    path(
        route='carrito',
        view=CarritoView.as_view(),
        name='carrito'
    ),

    path(
        route='carrito/<str:accion>',
        view=CarritoView.as_view(),
        name='carrito_accion'
    ),

    path(
        route='filtros',
        view=FiltrosView.as_view(),
        name='filtros'
    ),

    path(
        route='solicitud',
        view=SolicitudView.as_view(),
        name='solicitud'
    ),

    path(
        route='catalogo',
        view=CatalogoView.as_view(),
        name='catalogo'
    ),

    path(
        route="historial_solicitudes",
        view=HistorialSolicitudesView.as_view(),
        name='historial_solicitudes'
    ),

    path(
        route="detalles_orden/<int:id>",
        view=DetallesOrdenView.as_view(),
        name='detalles_orden'
    ),

    path(
        route='detalles_articulo/<int:id>/',
        view=DetallesArticuloView.as_view(),
        name='detalles_articulo'
    ),

    path(
        route='agregar_al_carrito/<int:articulo_id>/',
        view=AgregarAlCarritoView.as_view(),
        name='agregar_al_carrito'
    ),

    path(
        route='autorizacion_solicitudes/<int:id>/',
        view=AutorizacionSolicitudView.as_view(),
        name='autorizacion_solicitudes'
    ),

    path(
        route='cambiar_estado_orden/<int:id>/',
        view=CambiarEstadoOrdenView.as_view(),
        name='cambiar_estado_orden'
    ),

    path(
        route='actualizar_perfil',
        name='actualizar_perfil',
        view=ActualizarPerfilView.as_view()
    ),

    path(
        route='eliminar_del_carrito/<int:articulo_id>/',
        view=EliminarDelCarritoView.as_view(),
        name='eliminar_del_carrito'
    ),

    path(
        route='corresponsables',
        view=AgregarCorresponsablesView.as_view(),
        name='corresponsables'
    ),
]

handler403 = custom_403
handler404 = custom_404
