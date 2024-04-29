from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from .forms import UserLoginForm
from .views import AutorizacionSolitudView
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
        view=MenuView.as_view(),
        name='menu'
    ),

    path(
        route='carrito',
        view=CarritoView.as_view(),
        name='carrito'
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
        route='cancelar_orden',
        view=CancelarOrdenView.as_view(),
        name='cancelar_orden'
    ),

    path(
        route='autorizacion_solicitudes',
        view=AutorizacionSolitudView.as_view(),
        name='autorizacion_solicitudes'
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
