from django.contrib import admin
from django.contrib import messages
from import_export.admin import ImportExportModelAdmin

from .models import *


@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    search_fields = ('nombre', 'year')
    list_display = ('nombre', 'year', 'semestre')
    filter_horizontal = ('_alumnos', '_maestros', '_articulos')


@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    exclude = ('estado',)  #
    autocomplete_fields = ('prestatario', 'materia')
    filter_horizontal = ('_unidades', '_corresponsables')
    list_display = ('__str__', 'tipo', 'estado')
    search_fields = ['nombre']
    list_filter = ('estado', 'tipo')

    actions = ['entregar', 'devolver']

    # TODO: implementar estos metodos

    @admin.action(description='Marcar como entregado')
    def entregar(self, request, queryset):
        for orden in queryset:

            orden.entregar(request.user)

            if orden.entregada():
                messages.success(request, f'Orden {orden} entregada')
            else:
                messages.warning(request, f'No se pudo entregar la orden {orden}')

    @admin.action(description='Marcar como devuelto')
    def devolver(self, request, queryset):
        messages.error(request, "Ni esto")


@admin.register(Articulo)
class ArticuloAdmin(ImportExportModelAdmin):
    list_display = ('nombre', 'codigo', 'descripcion')
    search_fields = ['nombre', 'codigo']
    filter_horizontal = ('_categorias',)


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
            # messages.success(request, "Successfully made uppercase!")


@admin.register(Unidad)
class UnidadAdmin(admin.ModelAdmin):
    autocomplete_fields = ('articulo',)
    list_display = ('num_control', 'num_serie', 'articulo', 'estado')
    list_filter = ('estado',)
    search_fields = ['num_control', 'num_serie', 'articulo']


@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    search_fields = ['orden']
    list_display = ('orden', 'estado')
    autocomplete_fields = ('orden',)
    exclude = ('emisor',)

    def save_model(self, request, obj, form, change):
        # Registrar el usuario que está usando el admin como el emisor
        # del reporte
        obj.emisor = request.user
        super().save_model(request, obj, form, change)


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('numero_telefono',)
    search_fields = ['numero_telefono']


admin.site.register(Entrega)
admin.site.register(Devolucion)
admin.site.register(Categoria)
admin.site.register(AutorizacionOrden)
# admin.site.register(ArticuloCarrito)
# admin.site.register(CorresponsableOrden)
