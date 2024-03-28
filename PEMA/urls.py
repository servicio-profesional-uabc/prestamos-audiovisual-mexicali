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

]
