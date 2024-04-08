from django.urls import include, path
from . import views
from django.views.generic.base import TemplateView
from . forms import UserLoginForm
from django.contrib.auth.views import LoginView, LogoutView


urlpatterns = [
    # login
    path(
        route='',
        view=LoginView.as_view(
            template_name='login.html',
            authentication_form=UserLoginForm
        ),
        name='login'
    ),

    # logout
    path(
        route='logout',
        view=LogoutView.as_view(),
        name='logout'
    ),

    path(
        route='menu',
        view=views.Permisos.as_view(),
        name='menu'
    ),

    path(
        route='carrito',
        view=views.CarritoView.as_view(),
        name='carrito'
    ),
    path(
        route='filtros',
        view=views.FiltrosView.as_view(),
        name='filtros'
    ),

    path(
        route='solicitud',
        view=views.SolicitudView.as_view(),
        name='solicitud'
    ),

    path(
        route='catalogo',
        view=views.CatalogoView.as_view(),
        name='catalogo'
    ),
    path(
        route="historial_solicitudes",
        view=views.HistorialSolicitudesView.as_view(),
        name='historial_solicitudes'
    ),
    path(
        route="detalles_orden/<int:id>",
        view=views.DetallesOrdenView.as_view(),
        name='detalles_orden'
    ),
    
    
    path(
        route='detalles_articulo',
        view=views.DetallesArticuloView.as_view(),
        name='detalles_articulo'
    ),
    
    path(
        route='cancelar_orden',
        view=views.CancelarOrdenView.as_view(),
        name='cancelar_orden'
    ),
    path(
        route='recuperar_contrasena',
        view=views.RecuperarContrasenaView.as_view(),
        name='recuperar_contrasena'
    ),
]
