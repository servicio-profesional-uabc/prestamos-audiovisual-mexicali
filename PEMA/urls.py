from django.urls import include, path
from . import views
from django.views.generic.base import TemplateView

urlpatterns = [
    path(
        '',
        TemplateView.as_view(template_name='test.html'),
        name='test'
    ),


    path(
        route='prestatario.html',
        view=views.PrestatarioView.as_view(),
        name='prestatario'
    ),

    path(
        route='carrito.html',
        view=views.CarritoView.as_view(),
        name='carrito'
    ),
    path(
        route='solicitud.html',
        view=views.SolicitudView.as_view(),
        name='solicitud'
    ),

    path(
        route='historial.html',
        view=views.HistorialView.as_view(),
        name='historial'
    ),

    path(
        route='catalogo.html',
        view=views.CatalogoView.as_view(),
        name='catalogo'
    ),
    path(
        route="historial_solicitudes",
        view=views.HistorialSolicitudesView.as_view(),
        name='historial_solicitudes_html'
    ),
    path(
        route="detalles_orden",
        view=views.DetallesOrdenView.as_view(),
        name='detalles_orden_html'
    ),
    
    
    path(
        route='detalleArticulo.html',
        view=views.DetalleArticuloView.as_view(),
        name='detalleArticulo'
    ),
    
    path(
        route='cancelarOrden.html',
        view=views.CancelarOrdenView.as_view(),
        name='cancelarOrden'
    )
]
