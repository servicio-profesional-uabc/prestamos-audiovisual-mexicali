from django.urls import include, path
from . import views
from django.views.generic.base import TemplateView
from . forms import UserLoginForm
from django.contrib.auth.views import LoginView, LogoutView
from .views import cambiar_estado_ENTREGADO


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

    path(
        route='detalles_orden_autorizada/<int:id>/',
        view=views.DetallesOrdenAutorizadaView.as_view(),
        name='detalles_orden_autorizada'
    ),
    path(
        route='ordenes_devueltas/<int:id>/',
        view=views.OrdenesDevueltasView.as_view(),
        name='ordenes_devueltas'
    ),
    path(
        route='ordenes_devueltas',
        view=views.OrdenesDevueltasView.as_view(),
        name='ordenes_devueltas'
    ),
    path(
        route='detalles_orden_devuelta',
        view=views.DetallesOrdenDevueltaView.as_view(),
        name='detalles_orden_devuelta'
    ),
    path(
        route='detalles_orden_devuelta/<int:id>/',
        view=views.DetallesOrdenDevueltaView.as_view(),
        name='detalles_orden_devuelta'
    ),
    path(
        route='ordenes_prestadas',
        view=views.OrdenesPrestadasView.as_view(),
        name='ordenes_prestadas'
    ),
    path(
        route='ordenes_prestadas/<int:id>/',
        view=views.OrdenesPrestadasView.as_view(),
        name='ordenes_prestadas'
    ),
    path(
        route='ordenes_reportadas',
        view=views.OrdenesReportadasView.as_view(),
        name='ordenes_reportadas'
    ),
    path(
        route='ordenes_reportadas/<int:id>/',
        view=views.OrdenesReportadasView.as_view(),
        name='ordenes_reportadas'
    ),
    path(
        route='detalles_orden_reportada<int:id>',
        view=views.DetallesOrdenReportadaView.as_view(),
        name='detalles_orden_reportada'
    ),
    path(
       route='detalles_orden_reportada/<int:id>/<str:reporte>/',
        view=views.DetallesOrdenReportadaView.as_view(),
        name='detalles_orden_reportada'
    ),
    path(
        route='inventario',
        view=views.InventarioView.as_view(),
        name='inventario'
    ),
    path(
        route='usuarios_materias',
        view=views.UsuariosMateriasView.as_view(),
        name='usuarios_materias'
    ),
    path(
        route='ordenes_reportadas',
        view=views.OrdenesReportadasCordinadorView.as_view(),
        name='ordenes_reportadas'
    ),
    path(
        route='detalles_orden_prestada/<int:id>/',
        view=views.DetallesOrdenPrestadaView.as_view(),
        name='detalles_orden_prestada'
    ),
    path(
        route='reportar_orden/<int:id>/',
        view=views.ReportarOrdenView.as_view(),
        name='reportar_orden'
    ),
    path(
        route='principal',
        view=views.PrincipalAlmacenView.as_view(),
        name='principal',
    ),
    path('cambiar_estado/<int:orden_id>/<str:estado>/',
         view=views.cambiar_estado_ENTREGADO,
         name='cambiar_estado'),
    path('cambiar_estado_d/<int:orden_id>/<str:estado>/',
         view=views.cambiar_estado_DEVUELTO,
         name='cambiar_estado_d'),
    path('tramite_orden_reportada/<int:orden_id>',
         view=views.ReporteOrdenActivada.as_view(),
         name='tramite_orden_reportada'),
    path(
        route='desactivacion_reportadas/<int:id>/',
        view=views.DesactivarReportadasView.as_view(),
        name='desactivacion_reportadas'
    ),

]