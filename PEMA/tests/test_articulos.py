from django.test import TestCase
from django.contrib.auth.models import User
from django.test import TestCase
from PEMA.models import Articulo, Unidad


class ArticuloTestCase(TestCase):
    def test_crear_articulo(self):
        articulo = Articulo.objects.create(
            nombre="Titulo",
            codigo="123456"
        )

        unidad = Unidad.objects.create(
            articulo=articulo,
            codigo="1243234",
            estado=Unidad.Estado.ACTIVO
        )

        self.assertEquals(articulo, unidad.articulo)
