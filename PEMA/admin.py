from django.contrib import admin
from django.contrib import messages
from import_export.admin import ImportExportModelAdmin
from .models import *

class ReportedOrdersFilter(admin.SimpleListFilter):
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
    search_fields = ('nombre', 'year')
    list_display = ('nombre', 'year', 'semestre')
    filter_horizontal = ('_alumnos', '_maestros', '_articulos')

@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    exclude = ('estado',)
    autocomplete_fields = ('prestatario', 'materia')
    filter_horizontal = ('_unidades', '_corresponsables')
    list_display = ('prestatario', 'nombre', 'tipo', 'estado')
    search_fields = ['nombre']
    list_filter = ('estado', 'tipo', ReportedOrdersFilter)
    ordering = ('estado',)
    

    actions = ['entregar', 'devolver', 'cancelar']

    @admin.action(description='Marcar como entregado')
    def entregar(self, request, queryset):
        for orden in queryset:
            if(orden.entregada()):
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
            if(orden.devuelta()):
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
            if(orden.cancelada()):
                messages.warning(request, f'La orden {orden.nombre} ya se encuentra cancelada.')
                continue
            orden.cancelar()
            if orden.cancelada():
                messages.success(request, f'Orden {orden.nombre} cancelada')
            else:
                messages.warning(request, f'No se pudo cancelar la orden {orden.nombre}')

class ArticuloUnidadInline(admin.TabularInline):
    autocomplete_fields = ['articulo']
    model = Unidad
    extra = 0


@admin.register(Entrega)
class EntregaAdmin(admin.ModelAdmin):
    list_display = ('get_orden_nombre', 'emision')
    list_filter = ('orden', )
    def get_orden_nombre(self, obj):
        if (obj.orden.estado == EstadoOrden.ENTREGADA):
            return obj.orden.nombre
    
    get_orden_nombre.short_description = 'Nombre producción'

@admin.register(Devolucion)
class DevolucionAdmin(admin.ModelAdmin):
    list_display = ('get_orden_nombre', 'emision')
    list_filter = ('orden', )
    def get_orden_nombre(self, obj):
        if (obj.orden.estado == EstadoOrden.ENTREGADA):
            return obj.orden.nombre
    
    get_orden_nombre.short_description = 'Nombre producción'

@admin.register(Articulo)
class ArticuloAdmin(ImportExportModelAdmin):
    list_display = ('nombre', 'codigo', 'descripcion')
    search_fields = ['nombre', 'codigo']
    filter_horizontal = ('_categorias',)
    inlines = [ArticuloUnidadInline]

class ArticuloCarritoInline(admin.TabularInline):
    autocomplete_fields = ['articulo']
    model = ArticuloCarrito
    extra = 1

@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
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
    list_display = ('numero_telefono',)
    search_fields = ['numero_telefono']

class ArticuloInline(admin.TabularInline):
    model = Articulo._categorias.through
    extra = 1

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ['nombre']
    inlines = [ArticuloInline]


#admin.site.register(Entrega)
#admin.site.register(Devolucion)
admin.site.register(AutorizacionOrden)
