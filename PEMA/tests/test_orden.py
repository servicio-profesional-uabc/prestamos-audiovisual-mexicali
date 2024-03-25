from datetime import datetime
from django.test import TestCase

from django.utils.timezone import make_aware

from PEMA.models import Prestatario, Articulo, Orden


class TestOrden(TestCase):
    def setUp(self):
        self.prestataio = Prestatario.crear_usuario(
            id=0,
            username="<NAME>",
            password="<PASSWORD>",
        )

        self.articulo = Articulo.objects.create(
            nombre="Articulo 1",
            codigo="100"
        )

        self.unidad, _ =self.articulo.crear_unidad(
            num_control="000",
            num_serie="000"
        )

        self.orden = Orden.objects.create(
            prestatario=self.prestataio,
            inicio=make_aware(datetime(2024, 3, 16, 12)),
            final=make_aware(datetime(2024, 3, 16, 18)),
        )

    def test_agregar_unidad(self):
        unidad_orden, created = self.orden.agregar_unidad(self.unidad)

        self.assertTrue(created)


    def test_unidades(self):
        self.orden.agregar_unidad(self.unidad)

        a = self.orden.unidades()

        self.assertIn(self.unidad, a, "Articulo NO agregado")


