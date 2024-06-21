from django.contrib import admin
from django.contrib import messages
from import_export.admin import ImportExportModelAdmin

from .models import *


class ReportedOrdersFilter(admin.SimpleListFilter):
    """
    Este filtro permite mostrar órdenes que han sido reportadas y las que no han sido reportadas
    en el panel de administración de Django.
    """
    title = 'Estado de Reporte'
    parameter_name = 'reportadas'

    def lookups(self, request, model_admin):
        """
        Define las opciones del filtro para mostrar en el panel de administración.

        Returns:
            Tupla de tuplas con opciones ('valor_en_url', 'nombre_mostrado').
        """
        return (
            ('reportadas', 'Reportadas'),
            ('no_reportadas', 'No Reportadas'),
        )

    def queryset(self, request, queryset):
        """
        Aplica el filtro seleccionado a la queryset de órdenes.

        Args:
            request: Objeto de solicitud HTTP.
            queryset : QuerySet de órdenes sin filtrar.

        Returns:
            QuerySet filtrado según la opción seleccionada.
        """
        if self.value() == 'reportadas':
            return queryset.filter(reportes__isnull=False).distinct()
        if self.value() == 'no_reportadas':
            return queryset.filter(reportes__isnull=True)


@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    """
    Configuración de administración para el modelo Materia.

    Permite la gestión avanzada de materias en el panel de administración de Django.

    Attributes:
        search_fields: Define los campos por los cuales se puede realizar búsqueda.
        list_display : Especifica qué campos se muestran como columnas en la lista de materias.
        filter_horizontal : Permite seleccionar múltiples opciones en campos de relaciones Many-to-Many en formato horizontal.
    """
    search_fields = ('nombre', 'year')
    list_display = ('nombre', 'year', 'semestre')
    filter_horizontal = ('_alumnos', '_maestros', '_articulos')


@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    """
    Permite gestionar las órdenes en el panel de administración de Django.

    Attributes:
        exclude: Campos excluidos de la interfaz de administración.
        autocomplete_fields Campos que admiten autocompletado para selección.
        filter_horizontal: Campos Many-to-Many para la seleccion de unidades y corresponsables.
        list_display: Define qué campos se muestran como columnas en la lista de órdenes.
        search_fields: Campo por el cual se puede realizar búsqueda.
        list_filter: Permite filtrar las órdenes por estado, tipo y también por reportes.
        ordering: Define el orden predeterminado en el que se muestran las órdenes.
        actions: Acciones disponibles para realizar en las órdenes seleccionadas.

    Actions:
        entregar: Marca las órdenes seleccionadas como entregadas, si aún no lo están.
        devolver: Marca las órdenes seleccionadas como devueltas, si aún no lo están.
        cancelar: Cancela las órdenes seleccionadas, si aún no están canceladas.
    """
    exclude = ('estado', 'tipo')
    autocomplete_fields = ('prestatario', 'materia')
    filter_horizontal = ('_unidades', '_corresponsables')
    list_display = ('nombre', 'prestatario', 'tipo', 'estado', 'id')
    search_fields = ['nombre']
    list_filter = ('estado', 'tipo', ReportedOrdersFilter)
    ordering = ('estado',)

    actions = ['entregar', 'devolver', 'cancelar']

    @admin.action(description='Marcar como entregado')
    def entregar(self, request, queryset):
        """
        Marca las órdenes seleccionadas como ENTREGADA.

        Args:
            request: Objeto de solicitud HTTP.
            queryset: Conjunto de órdenes seleccionadas.

        Postconditions:
            Se muestra un mensaje de éxito o advertencia según el resultado de la operación.
        """
        for orden in queryset:
            if (orden.entregada()):
                messages.warning(request, f'La orden {orden.nombre} ya se encuentra entregada.')
                continue
            orden.entregar(request.user)
            if orden.entregada():
                messages.success(request, f'Orden {orden.nombre} entregada.')
            else:
                messages.warning(request, f'No se pudo entregar la orden {orden.nombre}.')

    @admin.action(description='Marcar como devuelto')
    def devolver(self, request, queryset):
        """
        Marca las órdenes seleccionadas como DEVUELTO.

        Args:
            request: Objeto de solicitud HTTP.
            queryset: Conjunto de órdenes seleccionadas.

        Postconditions:
            Se muestra un mensaje de éxito o advertencia según el resultado de la operación.
        """

        for orden in queryset:
            if (orden.devuelta()):
                messages.warning(request, f'La orden {orden.nombre} ya se encuentra devuelta.')
                continue
            orden.devolver(request.user)
            if orden.devuelta():
                messages.success(request, f'Orden {orden.nombre} devuelta')
            else:
                messages.warning(request, f'No se pudo devolver la orden {orden.nombre}')

    @admin.action(description='Marcar como cancelado')
    def cancelar(self, request, queryset):
        """
        CANCELA las órdenes seleccionadas.

        Args:
            request: Objeto de solicitud HTTP.
            queryset: Conjunto de órdenes seleccionadas.

        Postconditions:
            Se muestra un mensaje de éxito o advertencia según el resultado de la operación.
        """
        for orden in queryset:
            if (orden.cancelada()):
                messages.warning(request, f'La orden {orden.nombre} ya se encuentra cancelada.')
                continue
            orden.cancelar()
            if orden.cancelada():
                messages.success(request, f'Orden {orden.nombre} cancelada')
            else:
                messages.warning(request, f'No se pudo cancelar la orden {orden.nombre}')


class ArticuloUnidadInline(admin.TabularInline):
    """
    Configuración para mostrar unidades relacionadas con un artículo en línea dentro del panel de administración.

    Attributes:
        autocomplete_fields : Campos que admiten autocompletado para la selección de artículos.
        model : Modelo de datos asociado a las unidades.
        extra : Número adicional de formularios de unidades mostrados en la interfaz.
    """
    autocomplete_fields = ['articulo']
    model = Unidad
    extra = 0


@admin.register(Entrega)
class EntregaAdmin(admin.ModelAdmin):
    """
    Configuración de administración para el modelo Entrega.

    Permite gestionar las entregas en el panel de administración de Django.

    Attributes:
        list_display: Campos que se muestran como columnas en la lista de entregas.
        list_filter: Filtro para las entregas por orden.
    """
    list_display = ('get_orden_nombre', 'emision')
    list_filter = ('orden',)

    def get_orden_nombre(self, obj):
        """
        Obtiene el nombre de la orden asociada a la entrega si la orden está en estado APROBADA.

        Args:
            obj: Instancia de entrega.

        Returns:
            str: Nombre de la orden si está aprobada.
        """
        if (obj.orden.estado == EstadoOrden.APROBADA):
            return obj.orden.nombre

    get_orden_nombre.short_description = 'Nombre producción'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Filtra las órdenes que se pueden seleccionar para la entrega basadas en su estado APROBADA.

        Args:
            db_field: Campo de la base de datos.
            request: Objeto de solicitud HTTP.

        Returns:
            django.db.models.query.QuerySet: Conjunto de órdenes filtradas por estado APROBADA.
        """
        if db_field.name == "orden":
            kwargs["queryset"] = Orden.objects.filter(estado=EstadoOrden.APROBADA)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Devolucion)
class DevolucionAdmin(admin.ModelAdmin):
    """
    Permite gestionar las devoluciones en el panel de administración de Django.

    Attributes:
        list_display : Campos que se muestran como columnas en la lista de devoluciones.
        list_filter : Se filtran las devoluciones por orden.
    """
    list_display = ('get_orden_nombre', 'emision')
    list_filter = ('orden',)

    def get_orden_nombre(self, obj):
        """
        Obtiene el nombre de la orden asociada a la devolución si la orden está en estado ENTREGADA.

        Args:
            obj : Instancia de devolución.

        Returns:
            str: Nombre de la orden si está entregada.
        """
        if (obj.orden.estado == EstadoOrden.ENTREGADA):
            return obj.orden.nombre

    get_orden_nombre.short_description = 'Nombre producción'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Filtra las órdenes que se pueden seleccionar para la devolución basadas en su estado ENTREGADA.

        Args:
            db_field: Campo de la base de datos.
            request: Objeto de solicitud HTTP.
            **kwargs: Parámetros adicionales para el campo.

        Returns:
            django.db.models.query.QuerySet: Conjunto de órdenes filtradas por estado ENTREGADA.
        """
        if db_field.name == "orden":
            kwargs["queryset"] = Orden.objects.filter(estado=EstadoOrden.ENTREGADA)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Articulo)
class ArticuloAdmin(ImportExportModelAdmin):
    """
    Gestiona los artículos en el panel de administración de Django.

    Attributes:
        list_display: Campos que se muestran como columnas en la lista de artículos.
        search_fields: Campos por los cuales se puede realizar búsqueda.
        filter_horizontal: Campos Many-to-Many para la relacion.
        inlines: Define los inlines asociados para gestionar las unidades relacionadas con los artículos.
    """
    list_display = ('nombre', 'codigo', 'descripcion')
    search_fields = ['nombre', 'codigo']
    filter_horizontal = ('_categorias',)
    inlines = [ArticuloUnidadInline]


class ArticuloCarritoInline(admin.TabularInline):
    """
    Gestiona los artículos relacionados con un carrito en línea dentro del panel de administración de Django.

    Attributes:
        autocomplete_fields: Campos que admiten autocompletado para la selección de artículos.
        model : ArticuloCarrito.
        extra : Número adicional de formularios de artículos mostrados en la interfaz.
    """
    autocomplete_fields = ['articulo']
    model = ArticuloCarrito
    extra = 1


@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    """
    Gestiona los carritos en el panel de administración de Django.

    Attributes:
        actions: Accion disponible para realizar en los carritos seleccionados.
        list_display : Define qué campos se muestran como columnas en la lista de carritos.
        inlines: Define los inlines asociados para gestionar los artículos relacionados con los carritos.
        filter_horizontal : Campos para facilitar la selección de relacion.
    """
    actions = ['ordenar']
    list_display = ('prestatario', 'materia')
    inlines = [ArticuloCarritoInline]
    filter_horizontal = ('_corresponsables',)

    @admin.action(description='Ordenar artículos del carrito')
    def ordenar(self, request, queryset):
        """
        Ordena los artículos en los carritos seleccionados.

        Args:
            request: Objeto de solicitud HTTP.
            queryset: Conjunto de carritos seleccionados.
        """
        for obj in queryset:
            obj.ordenar()


@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    """
    Gestion de reportes en el panel de administración de Django.

        Attributes:
            search_fields : Campo para  realizar la búsqueda.
            list_display : Define qué campos se muestran como columnas en la lista de reportes.
            autocomplete_fields : Campos que admiten autocompletado para la selección de órdenes asociadas.
            exclude : Campos excluidos de la interfaz de administración.
            actions : Acciones disponibles para realizar en los reportes seleccionados.
        """
    search_fields = ['orden']
    list_display = ('orden', 'estado')
    autocomplete_fields = ('orden',)
    exclude = ('emisor',)
    actions = ['desactivar_reportes']

    def save_model(self, request, obj, form, change):
        """
        Guarda el modelo de reporte asociando al emisor actual.

        Args:
            request: Objeto de solicitud HTTP.
            obj: Objeto de reporte a guardar.
            form: Formulario utilizado para la operación.
            change: Indicador de si se está modificando un objeto existente.
        """
        obj.emisor = request.user
        super().save_model(request, obj, form, change)

    @admin.action(description='Desactivar reportes')
    def desactivar_reportes(self, request, queryset):
        """
        Desactiva los reportes seleccionados.

        Args:
            request: Objeto de solicitud HTTP.
            queryset: Conjunto de reportes seleccionados.
        """
        updated = 0
        for reporte in queryset:
            if reporte.estado == Reporte.Estado.ACTIVO:
                reporte.desactivar()
                updated += 1
        self.message_user(request, f'{updated} reporte(s) desactivado(s) exitosamente.', messages.SUCCESS)


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    """
    Gestiona los perfiles de usuarios en el panel de administración de Django.

    Attributes:
        list_display : Define el campo como columnas en la lista de perfiles.
        search_fields : Define el campo por el cual se puede realizar una bsuqueda.
    """
    list_display = ('numero_telefono',)
    search_fields = ['numero_telefono']


class ArticuloInline(admin.TabularInline):
    """
    Define la configuración para mostrar la relación entre Artículo y Categoría en línea dentro del panel de administración de Django.

    Attributes:
        model : Modelo de la relación entre Artículo y Categoría.
        extra : Número adicional de formularios de relación mostrados en la interfaz.
    """
    model = Articulo._categorias.through
    extra = 1


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    """
    Gestion de las categorías en el panel de administración de Django.

    Attributes:
        list_display: Campo que se muestra como columna en la lista de categorías.
        search_fields: Campo para realizar una busqueda.
        inlines: Inlines asociados para gestionar las relaciones de Artículo y Categoría.
    """
    list_display = ('nombre',)
    search_fields = ['nombre']
    inlines = [ArticuloInline]


admin.site.register(CorresponsableOrden)
