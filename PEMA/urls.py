from django.urls import include, path
from . import views
from django.views.generic.base import TemplateView


urlpatterns = [
    path(
        route='',
        view=views.LoginView.as_view(),
        name='login'
    ),

    path(
        route='menu',
        view=views.MenuView.as_view(),
        name='menu'
    ),

    path(
        route='carrito',
        view=views.CarritoView.as_view(),
        name='carrito'
    ),
    path(
        route='solicitud',
        view=views.SolicitudView.as_view(),
        name='solicitud'
    ),

    path(
        route='historial',
        view=views.HistorialView.as_view(),
        name='historial'
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
        route="detalles_orden",
        view=views.DetallesOrdenView.as_view(),
        name='detalles_orden'
    ),
    
    
    path(
        route='detalleArticulo',
        view=views.DetalleArticuloView.as_view(),
        name='detalleArticulo'
    ),
    
    path(
        route='cancelarOrden',
        view=views.CancelarOrdenView.as_view(),
        name='cancelarOrden'
    )
]
