from django.contrib import admin
from .models import *


class MateriaAdmin(admin.ModelAdmin):
    """
    Admin panel management for Alumni
    """
    list_display = ('nombre', 'year', 'semestre')
    filter_horizontal = ('_alumnos',)


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


admin.site.register(Perfil)
admin.site.register(Entrega)
admin.site.register(Devolucion)
admin.site.register(Carrito)
admin.site.register(Unidad)
admin.site.register(Categoria)
admin.site.register(AutorizacionOrden)
admin.site.register(ArticuloCarrito)
admin.site.register(CorresponsableOrden)
admin.site.register(Reporte)