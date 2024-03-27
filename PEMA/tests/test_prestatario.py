from django.contrib.auth.models import User, Group
from django.test import TestCase

from PEMA.models import Prestatario, Almacen, Orden
from PEMA.models import Carrito
from PEMA.models import Materia
from PEMA.models import Reporte

from django.utils.timezone import make_aware
from datetime import datetime


class TestPrestatario(TestCase):
    def setUp(self):
        # usuarios
        self.user_no_ordenes = Prestatario.crear_usuario(id=3, username="prestatario_NO", password="<PASSWORD>")
        self.user_prestatario = Prestatario.crear_usuario(id=1, username="prestatario", password="<PASSWORD>")
        self.user_almacen = Almacen.crear_usuario(id=2, username="almacen", password="<PASSWORD>")

        # ordenes
        self.orden1 = Orden.objects.create(
            prestatario=self.user_prestatario,
            lugar=Orden.Ubicacion.CAPUS,
            inicio=make_aware(datetime(2024, 10, 5)),
            final=make_aware(datetime(2024, 10, 5))
        )

        self.orden2 = Orden.objects.create(
            prestatario=self.user_prestatario,
            lugar=Orden.Ubicacion.EXTERNO,
            inicio=make_aware(datetime(2024, 10, 5)),
            final=make_aware(datetime(2024, 10, 5))
        )

    def test_lista_ordenes(self):
        # probar si no tiene ordenes
        prestatario_sin_ordenes = Prestatario.get_user(self.user_no_ordenes)
        self.assertEqual(len(prestatario_sin_ordenes.ordenes()), 0, msg="Prestatario ya tiene ordenes")

        # multiples ordenes
        prestatario = Prestatario.get_user(self.user_prestatario)
        ordenes = prestatario.ordenes()

        self.assertTrue(len(ordenes) == 2, msg="No se registraron las Ordenes")
        self.assertIn(self.orden1, ordenes, msg="No se registro la orden 1")
        self.assertIn(self.orden2, ordenes, msg="No se registro la orden 2")

    def test_lista_reportes(self):
        prestatario = Prestatario.get_user(self.user_prestatario)
        almacen = Almacen.get_user(self.user_almacen)

        # probar si no hay reportes
        self.assertEqual(len(prestatario.reportes()), 0, msg="El prestatario ya esta reportado")

        # un reporte
        almacen.reportar(orden=self.orden1, descripcion="Descripcion 1")
        self.assertEqual(len(prestatario.reportes()), 1, msg="El prestatario No se ha reportado")

        # multiples reportes
        almacen.reportar(orden=self.orden2, descripcion="Descripcion 2")
        self.assertEqual(len(prestatario.reportes()), 2, msg="El prestatario No se ha reportado varias veces")


    def test_lista_materias(self):
        materia1 = Materia.objects.create(
            nombre="Fotografia",
            periodo="2024-1"
        )

        materia2 = Materia.objects.create(
            nombre="Edicion y diseño",
            periodo="2024-1"
        )

        materia3 = Materia.objects.create(
            nombre="Animacion",
            periodo="2024-1"
        )

        materias = Materia.objects.all()

        self.assertIn(materia1, materias)
        self.assertIn(materia2, materias)
        self.assertIn(materia3, materias)

    def test_carrito(self):
        materia = Materia.objects.create(
            nombre="Fotografia",
            periodo="2024-1"
        )

        self.carrito = Carrito.objects.create(
            prestatario=self.user_prestatario,
            materia=materia,
            inicio=datetime.now(),
            final=datetime.now()
        )

        self.assertEqual(self.carrito.prestatario, self.user_prestatario)
        self.assertEqual(self.carrito.inicio, self.carrito.inicio)
        self.assertEqual(self.carrito.final, self.carrito.final)
        self.assertEqual(self.carrito.materia, materia)

    def test_suspendido(self):
        pass
