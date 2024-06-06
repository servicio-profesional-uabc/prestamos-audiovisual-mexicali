from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from .forms import UserLoginForm
from .views import ActualizarAutorizacion, AutorizacionSolitudView, AgregarAlCarritoView, AgregarCorresponsablesView
from .views import CancelarOrdenView
from .views import CarritoView
from .views import CatalogoView
from .views import DetallesArticuloView
from .views import DetallesOrdenAutorizadaView
from .views import DetallesOrdenDevueltaView
from .views import DetallesOrdenPrestadaView
from .views import DetallesOrdenReportadaView
from .views import DetallesOrdenView
from .views import FiltrosView
from .views import HistorialSolicitudesView
from .views import MenuView, ActualizarPerfilView
from .views import OrdenesDevueltasView
from .views import OrdenesPrestadasView
from .views import OrdenesReportadasView
from .views import PrincipalAlmacenView
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
    ),

    path(
        route='principal',
        view=PrincipalAlmacenView.as_view(),
        name='principal',
    ),

    path(
        route='detalles_orden_autorizada',
        view=DetallesOrdenAutorizadaView.as_view(),
        name='detalles_orden_autorizada',

    ),

    path(
        route='ordenes_prestadas',
        view=OrdenesPrestadasView.as_view(),
        name='ordenes_prestadas',

    ),

    path(
        route='detalles_orden_prestada',
        view=DetallesOrdenPrestadaView.as_view(),
        name='detalles_orden_prestada',

    ),

    path(
        route='ordenes_reportadas',
        view=OrdenesReportadasView.as_view(),
        name='ordenes_reportadas',
    ),

    path(
        route='detalles_orden_reportada',
        view=DetallesOrdenReportadaView.as_view(),
        name='detalles_orden_reportada',
    ),

    path(
        route='ordenes_devueltas',
        view=OrdenesDevueltasView.as_view(),
        name='ordenes_devueltas',

    ),

    path(
        route='detalles_orden_devuelta',
        view=DetallesOrdenDevueltaView.as_view(),
        name='detalles_orden_devuelta',

    ),

    path(
        route='corresponsables',
        view=AgregarCorresponsablesView.as_view(),
        name='corresponables'
    )
]

# https://github.com/fabiocaccamo/django-admin-interface/issues/4
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
