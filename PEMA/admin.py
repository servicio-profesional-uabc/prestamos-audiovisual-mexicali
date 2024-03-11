from django.contrib import admin
from .models import *


admin.site.register(Prestatario)
admin.site.register(Almacen)
admin.site.register(Maestro)


admin.site.register(Carrito)
admin.site.register(Materia)
admin.site.register(Orden)
admin.site.register(Reporte)
admin.site.register(Articulo)
admin.site.register(Unidad)
admin.site.register(Categoria)
admin.site.register(AutorizacionAlmacen)
admin.site.register(AutorizacionCoordinador)
admin.site.register(ArticuloCarrito)
admin.site.register(ArticuloMateria)
admin.site.register(CategoriaArticulo)
