from django.contrib import admin, messages

from .models import *


@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    """
    Admin panel management for Alumni
    """
    list_display = ('nombre', 'year', 'semestre')
    filter_horizontal = ('_alumnos', '_maestros', '_articulos')


@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    """
    Admin panel management for Alumni
    """
    list_display = ('nombre', 'tipo', 'inicio', 'emision')
    filter_horizontal = ('_unidades',)


@admin.register(Articulo)
class ArticuloAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'descripcion')
    search_fields = ['nombre', 'codigo']
    filter_horizontal = ('_categorias',)


@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ('prestatario', 'materia')
    actions = ['ordenar']

    @admin.action(description='Ordenar artículos del carrito')
    def ordenar(self, request, queryset):
        for obj in queryset:
            obj.ordenar()
            # messages.success(request, "Successfully made uppercase!")


@admin.register(Unidad)
class UnidadAdmin(admin.ModelAdmin):
    list_display = ('num_control', 'num_serie', 'articulo', 'estado')
    search_fields = ['num_control', 'num_serie', 'articulo']


admin.site.register(Perfil)
admin.site.register(Entrega)
admin.site.register(Devolucion)
admin.site.register(Categoria)
admin.site.register(AutorizacionOrden)
# admin.site.register(ArticuloCarrito)
admin.site.register(CorresponsableOrden)
admin.site.register(Reporte)
