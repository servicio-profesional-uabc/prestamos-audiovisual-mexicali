from django.contrib import admin
from .models import *

admin.site.register(Prestatario)
admin.site.register(Almacen)
admin.site.register(Maestro)
admin.site.register(Coordinador)
admin.site.register(Perfil)

admin.site.register(Entrega)
admin.site.register(Devolucion)
admin.site.register(Carrito)


class MateriaAdmin(admin.ModelAdmin):
    """
    Admin panel management for Alumni
    """
    list_display = ('nombre', 'year', 'semestre')
    filter_horizontal = ('_alumnos',)


admin.site.register(Materia, MateriaAdmin)

admin.site.register(Orden)
admin.site.register(Reporte)


class ArticuloAdmin(admin.ModelAdmin):
    """
    Admin panel management for Alumni
    """
    list_display = ('nombre', 'codigo', 'descripcion')
    filter_horizontal = ('_categorias',)


admin.site.register(Articulo, ArticuloAdmin)

admin.site.register(Unidad)
admin.site.register(Categoria)

admin.site.register(AutorizacionOrden)

admin.site.register(ArticuloCarrito)
admin.site.register(ArticuloMateria)
admin.site.register(UnidadOrden)
admin.site.register(CorresponsableOrden)
