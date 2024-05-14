from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from .forms import UserLoginForm
from .views import ActualizarAutorizacion, AutorizacionSolitudView, AgregarAlCarritoView
from .views import CancelarOrdenView
from .views import CarritoView
from .views import CatalogoView
from .views import DetallesArticuloView
from .views import DetallesOrdenView
from .views import FiltrosView
from .views import HistorialSolicitudesView
from .views import MenuView, ActualizarPerfilView
from .views import SolicitudView

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
    path('logout/', LogoutView.as_view(), name='logout'),

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
        route='cancelar_orden',
        view=CancelarOrdenView.as_view(),
        name='cancelar_orden'
    ),

    path(
        route='autorizacion_solicitudes/<str:type>/<int:id>/',
        view=AutorizacionSolitudView.as_view(),
        name='autorizacion_solicitudes'
    ),

    path(
        route='actualizar_autorizacion/<str:type>/<str:state>/<int:id>',
        view=ActualizarAutorizacion.as_view(),
        name='actualizar_autorizacion'
    ),

    path(
        route='actualizar_perfil',
        name='actualizar_perfil',
        view=ActualizarPerfilView.as_view()
    )
]

# https://github.com/fabiocaccamo/django-admin-interface/issues/4
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
