from datetime import datetime
from unittest import TestCase

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

        self.unidad =self.articulo.crear_unidad(
            num_control="000",
            num_serie="000"
        )

    def test_orden_unidades(self):

        orden = Orden.objects.create(
            prestataio=self.prestataio,
            inicio=make_aware(datetime(2024, 3, 16, 12)),
            final=make_aware(datetime(2024, 3, 16, 18)),
        )

        orden.agregar_orden(self.unidad)

        self.assertIn(self.unidad, orden.unidades(), "Articulo NO agregado")


