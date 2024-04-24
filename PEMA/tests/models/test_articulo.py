from datetime import datetime

from django.test import TestCase
from django.utils.timezone import make_aware

from PEMA.models import Articulo, Prestatario
from PEMA.models import Materia
from PEMA.models import Categoria
from PEMA.models import Orden


class TestArticulo(TestCase):

    @staticmethod
    def generar_fechas(hora):
        return make_aware(datetime(2024, 3, 16, 12 + hora))

    def setUp(self):
        self.prestatario = Prestatario.crear_usuario(id="123",username="test", password="<PASSWORD>")

        self.articulo = Articulo.objects.create(
            nombre="articulo 1",
            codigo="codigo 1"
        )

        self.unidad, _ = self.articulo.crear_unidad(
            num_control="num_control 1",
            num_serie="num_series 2"
        )

        self.materia = Materia.objects.create(nombre="fotografia", year=2022, semestre=1)

        self.orden_antes = Orden.objects.create(
            prestatario=self.prestatario,
            materia=self.materia,
            lugar="Prueba antes",
            inicio=self.generar_fechas(-1),
            final=self.generar_fechas(1)
        )

        self.orden_despues = Orden.objects.create(
            prestatario=self.prestatario,
            materia=self.materia,
            lugar="prueba despues",
            inicio=self.generar_fechas(0),
            final=self.generar_fechas(1)
        )

        self.orden_antes.agregar_unidad(unidad=self.unidad)
        self.orden_despues.agregar_unidad(unidad=self.unidad)

    def test_unidades(self):
        unidades = self.articulo.unidades()

        self.assertIn(self.unidad, unidades, "Unidades no registradas de manera correcta")
        self.assertEqual(len(unidades), 1, "Unidades no registradas")

    def test_categorias(self):
        # crear categorías
        categoria1 = Categoria.objects.create(nombre="Categoría 1")
        categoria2 = Categoria.objects.create(nombre="Categoría 2")

        # agregar el artículo
        categoria1.agregar(self.articulo)
        categoria2.agregar(self.articulo)

        # test
        categorias_articulo = self.articulo.categorias()

        self.assertIn(categoria1, categorias_articulo, msg="La categoría no se agrego correctamente")
        self.assertEqual(len(categorias_articulo), 2, msg="Numero incorrecto de categorías")

    def test_materia(self):
        self.materia.agregar_articulo(self.articulo)

        self.assertIn(self.materia, self.articulo.materias())
