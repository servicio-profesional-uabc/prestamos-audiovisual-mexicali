from django.urls import include, path
from . import views
from django.views.generic.base import TemplateView

urlpatterns = [
    path(
        'accounts/', include('django.contrib.auth.urls')
    ),
    path(
        '', TemplateView.as_view(template_name='index.html'), name='index'
    ),
    path(
        route='test/',
        view=views.test,
        name='test'
    ),

    path(
        route='prestatario',
        view=views.PrestatarioView.as_view(),
        name='prestatario_html'
    ),

    path(
        route='carrito',
        view=views.CarritoView.as_view(),
        name='carrito_html'
    ),
    path(
        route='solicitud',
        view=views.SolicitudView.as_view(),
        name='solicitud_html'
    ),
    

]
