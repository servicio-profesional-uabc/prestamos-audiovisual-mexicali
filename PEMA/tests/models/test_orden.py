from datetime import datetime

from django.test import TestCase
from django.utils.timezone import make_aware

from PEMA.models import Prestatario, Articulo, Orden, Reporte, Almacen, Materia


class TestOrden(TestCase):
    def setUp(self):
        # usuarios
        self.prestataio = Prestatario.crear_usuario(id=0, username="<NAME>", password="<PASSWORD>")
        self.almacen = Almacen.crear_usuario(id=1, username="<NAME2>", password="<PASSWORD>")

        # crear articulos
        self.articulo1 = Articulo.objects.create(nombre="Articulo 1", codigo="100")
        self.articulo2 = Articulo.objects.create(nombre="Articulo 2", codigo="200")

        # crear unidades
        self.unidad1, _ = self.articulo1.crear_unidad(num_control="000", num_serie="000")
        self.unidad2, _ = self.articulo2.crear_unidad(num_control="100", num_serie="200")

        materia = Materia.objects.create(nombre="Fotografia", year=2022, semestre=1)

        self.orden = Orden.objects.create(prestatario=self.prestataio, materia=materia, inicio=make_aware(datetime(2024, 3, 16, 12)),
                                          final=make_aware(datetime(2024, 3, 16, 18)), )

    def test_agregar_unidad(self):
        self.orden.agregar_unidad(self.unidad1)

        self.assertIn(self.unidad1, self.orden.unidades())

    def test_unidades(self):
        self.orden.agregar_unidad(self.unidad1)

        self.assertIn(member=self.unidad1, container=self.orden.unidades(), msg="Unidad No registrada")

    def test_articulo(self):
        # agregar el objeto de manera repetida
        self.orden.agregar_unidad(self.unidad1)
        self.orden.agregar_unidad(self.unidad1)

        self.assertEqual(len(self.orden.articulos()), 1, msg="Hay mas articulos registrados")

        # agregar un objeto nuevo
        self.orden.agregar_unidad(self.unidad2)
        self.assertEqual(len(self.orden.articulos()), 2, msg="Hay menos articulos registrados")

        self.assertIn(member=self.articulo1, container=self.orden.articulos(), msg="Articulo1 No existe en la orden")
        self.assertIn(member=self.articulo2, container=self.orden.articulos(), msg="Articulo2 No existe en la orden")

    def test_reporte(self):
        almacen = Almacen.get_user(self.almacen)

        # Si no hay reporte
        self.assertIsNone(self.orden.reporte(), msg="Ya existe un reporte")

        # si hay un reporte
        self.orden.reportar(almacen=almacen, descripcion="Nada")
        self.assertIsNotNone(obj=self.orden.reporte(), msg="No existe un reporte")

        # verificar que una orden no se puede reportar 2 veces
        self.orden.reportar(almacen=almacen, descripcion="Nada")
        self.assertEqual(len(Reporte.objects.filter(orden=self.orden)), 1)
