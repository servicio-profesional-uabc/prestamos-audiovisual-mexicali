import tablib
from django.contrib import admin
from django.contrib import messages
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin

from .models import *


class UserResource(resources.ModelResource):
    # Define los campos y los nombres de los headers personalizados
    username = fields.Field(attribute='first_name', column_name='NOMBRE_DEL_ALUMNO')
    first_name = fields.Field(attribute='username', column_name='MATRICULA')

    class Meta:
        model = User
        skip_unchanged = True
        report_skipped = False
        header_row = 23
        import_id_fields = ('username',)
        fields = ('NOMBRE_DEL_ALUMNO', 'MATRICULA')

    def import_data(self, dataset, dry_run=False, raise_errors=False, use_transactions=None, collect_failed_rows=False,
                    **kwargs):
        subseccion = dataset[23:len(dataset) - 4]

        data = tablib.Dataset()
        data.headers = ['NOMBRE_DEL_ALUMNO', 'MATRICULA']
        for i in subseccion:
            data.append([i[1], i[8]])

        cleaned_data = data
        print(cleaned_data)
        return super().import_data(cleaned_data, dry_run, raise_errors, use_transactions, collect_failed_rows, **kwargs)


@admin.register(Prestatario)
class UserAdmin(ImportExportModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email')
    resource_class = UserResource


class ReportedOrdersFilter(admin.SimpleListFilter):
    """
   Permitir a los administradores filtrar las órdenes en función de si han sido reportadas o no.

    Este filtro se añade al panel de administración de Django y proporciona opciones para ver órdenes que han
    sido reportadas y órdenes que no lo han sido.
    """
    title = 'Estado de Reporte'
    parameter_name = 'reportadas'

    def lookups(self, request, model_admin):
        return (
            ('reportadas', 'Reportadas'),
            ('no_reportadas', 'No Reportadas'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'reportadas':
            return queryset.filter(reportes__isnull=False).distinct()
        if self.value() == 'no_reportadas':
            return queryset.filter(reportes__isnull=True)


@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    """
    Se encarga de administrar las materias.

    Permite buscar materias por nombre y año, mostrar en la lista el nombre, año y semestre de las materias,
    y gestionar las relaciones Many-to-Many con alumnos, maestros y artículos.
    """
    search_fields = ('nombre', 'year')
    list_display = ('nombre', 'year', 'semestre')
    filter_horizontal = ('_alumnos', '_maestros', '_articulos')


class CorresponsableOrdenInline(admin.TabularInline):
    """
    Muestra y gestiona unidades asociadas a un artículo.

    Ofrece una interfaz para gestionar unidades vinculadas a los articulos artículos.
    """
    autocomplete_fields = ('autorizador',)
    model = CorresponsableOrden
    extra = 1


@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    """
    Gestionar las ordenes en el panel de administración de Django.

    Proporciona funcionalidades como autocompletado para prestatario y materia,
    búsqueda por nombre de orden, filtros por estado y tipo de orden, y acciones para marcar órdenes como entregadas,
    devueltas o canceladas.
    """
    exclude = ('estado', 'tipo')
    autocomplete_fields = ('prestatario', 'materia')
    filter_horizontal = ('_unidades',)
    list_display = ('nombre', 'prestatario', 'tipo', 'estado', 'id')
    search_fields = ['nombre']
    inlines = [CorresponsableOrdenInline]
    list_filter = ('estado', 'tipo', ReportedOrdersFilter)
    ordering = ('estado',)

    actions = ['entregar', 'devolver', 'cancelar']

    @admin.action(description='Marcar como entregado')
    def entregar(self, request, queryset):

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
        for orden in queryset:
            if orden.cancelada():
                messages.warning(request, f'La orden {orden.nombre} ya se encuentra cancelada.')
                continue
            orden.cancelar()
            if orden.cancelada():
                messages.success(request, f'Orden {orden.nombre} cancelada')
            else:
                messages.warning(request, f'No se pudo cancelar la orden {orden.nombre}')


class ArticuloUnidadInline(admin.TabularInline):
    """
    Muestra y gestiona unidades asociadas a un artículo.

    Ofrece una interfaz para gestionar unidades vinculadas a los articulos artículos.

    """
    autocomplete_fields = ['articulo']
    model = Unidad
    extra = 0


@admin.register(Entrega)
class EntregaAdmin(admin.ModelAdmin):
    """
    Facilitar la gestión de entregas.

    Muestra detalles de las entregas como nombre de la orden y fecha de emisión,
    y filtra órdenes disponibles según su estado.
    """
    list_display = ('get_orden_nombre', 'emision')
    list_filter = ('orden',)

    def get_orden_nombre(self, obj):
        if (obj.orden.estado == EstadoOrden.APROBADA):
            return obj.orden.nombre

    get_orden_nombre.short_description = 'Nombre producción'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):

        if db_field.name == "orden":
            kwargs["queryset"] = Orden.objects.filter(estado=EstadoOrden.APROBADA)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Devolucion)
class DevolucionAdmin(admin.ModelAdmin):
    """
    Muestra detalles de devoluciones y filtra órdenes disponibles según su estado.
    """
    list_display = ('get_orden_nombre', 'emision')
    list_filter = ('orden',)

    def get_orden_nombre(self, obj):
        if (obj.orden.estado == EstadoOrden.ENTREGADA):
            return obj.orden.nombre

    get_orden_nombre.short_description = 'Nombre producción'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "orden":
            kwargs["queryset"] = Orden.objects.filter(estado=EstadoOrden.ENTREGADA)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Articulo)
class ArticuloAdmin(ImportExportModelAdmin):
    """
    Permite buscar un articulo por nombre y código, muestra información y
     gestiona las relaciones con categorías.

    """
    list_display = ('nombre', 'codigo', 'descripcion')
    search_fields = ['nombre', 'codigo']
    filter_horizontal = ('_categorias',)
    inlines = [ArticuloUnidadInline]


class ArticuloCarritoInline(admin.TabularInline):
    """
    Ofrece una interfaz para seleccionar y gestionar artículos asociados a carritos.
    """
    autocomplete_fields = ['articulo']
    model = ArticuloCarrito
    extra = 1


@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    """
    Gestiona los carritos mostrando detalles como prestatario y materia,
    al igual que gestiona relaciones y permite la acción de ordenar artículos en carritos seleccionados.
    """
    actions = ['ordenar']
    list_display = ('prestatario', 'materia')
    inlines = [ArticuloCarritoInline]
    filter_horizontal = ('_corresponsables',)

    @admin.action(description='Ordenar artículos del carrito')
    def ordenar(self, request, queryset):
        for obj in queryset:
            obj.ordenar()


@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    """
    Se administrna los reportes.

    Muestra detalles como estado del reporte,
    gestiona relación con órdenes, excluye el campo del emisor y realiza acciones como desactivar reportes.
        """
    search_fields = ['orden']
    list_display = ('orden', 'estado')
    autocomplete_fields = ('orden',)
    exclude = ('emisor',)
    actions = ['desactivar_reportes']

    def save_model(self, request, obj, form, change):
        obj.emisor = request.user
        super().save_model(request, obj, form, change)

    @admin.action(description='Desactivar reportes')
    def desactivar_reportes(self, request, queryset):
        updated = 0
        for reporte in queryset:
            if reporte.estado == Reporte.Estado.ACTIVO:
                reporte.desactivar()
                updated += 1
        self.message_user(request, f'{updated} reporte(s) desactivado(s) exitosamente.', messages.SUCCESS)


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    """
    Gestionar perfiles de usuarios en el panel de administración de Django.
    Mostrando detalles como número de teléfono y permite búsqueda por este campo.

    """
    list_display = ('usuario',)
    search_fields = ['numero_telefono']


class ArticuloInline(admin.TabularInline):
    """
    Muestra y gestiona la relación entre artículos y categorías .

    """
    model = Articulo._categorias.through
    extra = 1


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    """
    Administra las categorías.
    Mostrando detalles como nombre de categorías, permite búsqueda por nombre y gestiona relaciones con artículos.

    """
    list_display = ('nombre',)
    search_fields = ['nombre']
    inlines = [ArticuloInline]
