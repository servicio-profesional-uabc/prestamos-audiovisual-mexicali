from django.contrib import admin, messages

from .models import *


class MateriaAdmin(admin.ModelAdmin):
    """
    Admin panel management for Alumni
    """
    list_display = ('nombre', 'year', 'semestre')
    filter_horizontal = ('_alumnos', '_maestros', '_articulos')


admin.site.register(Materia, MateriaAdmin)


class OrdenAdmin(admin.ModelAdmin):
    """
    Admin panel management for Alumni
    """
    list_display = ('nombre', 'tipo', 'inicio', 'emision')
    filter_horizontal = ('_unidades',)


admin.site.register(Orden, OrdenAdmin)


class ArticuloAdmin(admin.ModelAdmin):
    """
    Admin panel management for Alumni
    """
    list_display = ('nombre', 'codigo', 'descripcion')
    filter_horizontal = ('_categorias',)


admin.site.register(Articulo, ArticuloAdmin)


@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ('prestatario', 'materia')
    actions = ['uppercase']

    @admin.action(description='Make selected persons uppercase')
    def uppercase(self, request, queryset):
        for obj in queryset:
            obj.ordenar()
            messages.success(request, "Successfully made uppercase!")


admin.site.register(Perfil)
admin.site.register(Entrega)
admin.site.register(Devolucion)
admin.site.register(Unidad)
admin.site.register(Categoria)
admin.site.register(AutorizacionOrden)
admin.site.register(ArticuloCarrito)
admin.site.register(CorresponsableOrden)
admin.site.register(Reporte)