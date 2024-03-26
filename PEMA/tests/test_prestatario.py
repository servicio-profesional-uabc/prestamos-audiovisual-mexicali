from django.contrib.auth.models import User, Group
from django.test import TestCase

from PEMA.models import Prestatario, Almacen, Orden
from PEMA.models import Carrito
from PEMA.models import Materia
from PEMA.models import Reporte

from django.utils.timezone import make_aware
from datetime import datetime


class TestUsers(TestCase):
    def setUp(self):
        grupo, _ = Prestatario.crear_grupo()

        self.user_normal = User.objects.create_user(
            id=0,
            username="sin_rol",
            password="<PASSWORD>"
        )

        self.user_prestatario = Prestatario.crear_usuario(
            id=1,
            username="prestatario",
            password="<PASSWORD>"
        )

        self.user_almacen = Almacen.crear_usuario(
            id=2,
            username="almacen",
            password="<PASSWORD>"
        )

    def test_lista_ordenes(self):
        prestatario = Prestatario.objects.get(pk=self.user_prestatario.pk)

        # probar si no tiene ordenes
        self.assertEqual(len(prestatario.ordenes()), 0, msg="Prestatario ya tiene ordenes")

        orden1 = Orden.objects.create(
            prestatario=self.user_prestatario,
            lugar=Orden.Ubicacion.CAPUS,
            inicio=make_aware(datetime(2024, 10, 5)),
            final=make_aware(datetime(2024, 10, 5))
        )

        orden2 = Orden.objects.create(
            prestatario=self.user_prestatario,
            lugar=Orden.Ubicacion.EXTERNO,
            inicio=make_aware(datetime(2024, 10, 5)),
            final=make_aware(datetime(2024, 10, 5))
        )

        ordenes = prestatario.ordenes()
        self.assertTrue(len(ordenes) == 2, msg="No se registraron las Ordenes")
        self.assertIn(orden1, ordenes, msg="No se registro la orden 1")
        self.assertIn(orden2, ordenes, msg="No se registro la orden 2")

    def test_lista_reportes(self):
        pass

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
