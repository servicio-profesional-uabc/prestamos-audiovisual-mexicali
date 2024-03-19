from datetime import datetime

from django.test import TestCase
from django.utils.timezone import make_aware

from PEMA.models import Articulo
from PEMA.models import Categoria
from PEMA.models import Orden
from PEMA.models import UnidadOrden
from PEMA.models import Prestatario


class TestArticulo(TestCase):

    @staticmethod
    def generar_fechas(hora):
        return make_aware(datetime(2024, 3, 16, 12 + hora))

    def setUp(self):
        self.user = Prestatario.crear_usuario(
            id=0,
            username="sin_rol",
            password="<PASSWORD>"
        )

        self.articulo = Articulo.objects.create(
            nombre="articulo 1",
            codigo="codigo 1"
        )

        self.unidad, _ = self.articulo.crear_unidad(
            num_control="num_control 1",
            num_serie="num_series 2"
        )

        self.orden_antes = Orden.objects.create(
            prestatario=self.user,
            lugar="Prueba antes",
            inicio=self.generar_fechas(-1),
            final=self.generar_fechas(1)
        )

        self.orden_despues = Orden.objects.create(
            prestatario=self.user,
            lugar="prueba despues",
            inicio=self.generar_fechas(0),
            final=self.generar_fechas(1)
        )

        self.orden_antes.agregar(unidad=self.unidad)
        self.orden_despues.agregar(unidad=self.unidad)

    def test_unidades(self):
        unidades = self.articulo.unidades()

        self.assertEqual(unidades[0], self.unidad, "Unidades no registradas de manera correcta")
        self.assertEqual(len(unidades), 1, "Unidades no registradas")


    def test_categorias(self):
        categoria1 = Categoria.objects.create(
            nombre="Categoria 1"
        )

        categoria2 = Categoria.objects.create(
            nombre="Categoria 2"
        )

        categoria1.agregar(self.articulo)
        categorias = self.articulo.categorias()

        self.assertEqual(
            categorias[0],
            categoria1,
            msg="La categoria no se agrego correctamente"
        )

        categoria2.agregar(self.articulo)
        categorias = self.articulo.categorias()

        self.assertEqual(
            len(categorias),
            2,
            msg="Numero incorrecto de categorias"
        )







    #def test_disponible(self):
     #   for a in self.articulo.disponible(
      #          inicio=self.generar_fechas(0),
       #         final=self.generar_fechas(1)
        #):
         #   print(a.lugar)
