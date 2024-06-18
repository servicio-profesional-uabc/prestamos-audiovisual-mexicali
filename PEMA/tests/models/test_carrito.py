from datetime import datetime

from django.test import TestCase
from django.utils.timezone import make_aware

from PEMA.models import Prestatario, Materia, Carrito, Articulo, Orden


class TestCarrito(TestCase):
    def setUp(self):
        self.user = Prestatario.objects.create(username="test_user", password="test_password")
        self.materia = Materia.objects.create(nombre="fotografia", year=2022, semestre=1)
        self.articulo = Articulo.objects.create(nombre="Artículo de prueba", codigo="0000-0000")

    def test_agregar_articulo(self):
        carrito = Carrito.objects.create(prestatario=self.user, materia=self.materia,
                                         inicio=make_aware(datetime(2024, 3, 16, 12)),
                                         final=make_aware(datetime(2024, 3, 16, 18)))

        # Agregar un artículo al carrito
        carrito.agregar(articulo=self.articulo, unidades=1)
        self.assertEqual(carrito.articulos_carrito().count(), 1)

        # Agregar el mismo artículo con más unidades
        carrito.agregar(articulo=self.articulo, unidades=2)
        self.assertEqual(carrito.articulos_carrito().count(), 1)

        # Agregar un nuevo artículo al carrito
        otro_articulo = Articulo.objects.create(nombre="Otro artículo de prueba", codigo="0000-0001")
        carrito.agregar(articulo=otro_articulo, unidades=3)
        self.assertEqual(carrito.articulos_carrito().count(), 2)

    def test_articulos_carrito(self):
        carrito = Carrito.objects.create(prestatario=self.user, materia=self.materia,
                                         inicio=make_aware(datetime(2024, 3, 16, 12)),
                                         final=make_aware(datetime(2024, 3, 16, 18)))

        # Verificar que el carrito esté vacío al inicio
        self.assertEqual(carrito.articulos_carrito().count(), 0)

        # Agregar un artículo y verificar que esté en el carrito
        carrito.agregar(articulo=self.articulo, unidades=1)
        self.assertEqual(carrito.articulos_carrito().count(), 1)
        self.assertIn(self.articulo, carrito.articulos())

    def test_ordenar_carrito(self):
        carrito = Carrito.objects.create(prestatario=self.user, materia=self.materia,
                                         inicio=make_aware(datetime(2024, 3, 16, 12)),
                                         final=make_aware(datetime(2024, 3, 16, 18)))

        # Ordenar el carrito vacío
        carrito.ordenar()

        # Agregar un artículo al carrito
        carrito.agregar(articulo=self.articulo, unidades=1)

        # Ordenar el carrito cuando no hay unidades
        carrito.ordenar()
        self.assertEqual(Carrito.objects.all().count(), 1)

        # ordenar carrito cuando si hay unidades
        self.articulo.crear_unidad("num_control", "num_serie")
        carrito.ordenar()
        self.assertEqual(Carrito.objects.all().count(), 0)

        # Verificar que se haya creado una Orden
        self.assertEqual(Orden.objects.all().count(), 1)

    def test_crear_orden_desde_carrito(self):
        carrito = Carrito.objects.create(prestatario=self.user, materia=self.materia,
                                         nombre="Producción de prueba",
                                         lugar="CA",
                                         descripcion_lugar="Estudio 1",
                                         descripcion="Descripción de prueba",
                                         inicio=make_aware(datetime(2024, 3, 16, 12)),
                                         final=make_aware(datetime(2024, 3, 16, 18)))

        # Crear la orden desde el carrito
        orden = carrito.crear_orden_desde_carrito()

        # Verificar que la orden se haya creado correctamente
        self.assertEqual(orden.nombre, carrito.nombre)
        self.assertEqual(orden.prestatario, carrito.prestatario)
        self.assertEqual(orden.lugar, carrito.lugar)
        self.assertEqual(orden.descripcion_lugar, carrito.descripcion_lugar)
        self.assertEqual(orden.materia, carrito.materia)
        self.assertEqual(orden.maestro, carrito.maestro)
        self.assertEqual(orden.inicio, carrito.inicio)
        self.assertEqual(orden.final, carrito.final)
        self.assertEqual(orden.descripcion, carrito.descripcion)

    def test_numero_total_unidades(self):
        carrito = Carrito.objects.create(prestatario=self.user, materia=self.materia,
                                         inicio=make_aware(datetime(2024, 3, 16, 12)),
                                         final=make_aware(datetime(2024, 3, 16, 18)))

        # Inicialmente el carrito está vacío
        self.assertEqual(carrito.numero_total_unidades(), 0)

        # Agregar artículos al carrito
        carrito.agregar(articulo=self.articulo, unidades=2)
        self.assertEqual(carrito.numero_total_unidades(), 2)

        otro_articulo = Articulo.objects.create(nombre="Otro artículo de prueba", codigo="0000-0001")
        carrito.agregar(articulo=otro_articulo, unidades=3)
        self.assertEqual(carrito.numero_total_unidades(), 5)
