from datetime import datetime

from django.test import TestCase
from django.utils.timezone import make_aware

from PEMA.models import Carrito, Ubicacion
from PEMA.models import Materia
from PEMA.models import Prestatario, Almacen, Orden


class TestPrestatario(TestCase):
    def setUp(self):
        # usuarios
        self.user_no_ordenes = Prestatario.crear_usuario(id=3, username="prestatario_NO", password="<PASSWORD>")
        self.user_prestatario = Prestatario.crear_usuario(id=1, username="prestatario", password="<PASSWORD>")
        self.user_almacen = Almacen.crear_usuario(id=2, username="almacen", password="<PASSWORD>")

        self.materia = Materia.objects.create(nombre="Fotografia2", year=2022, semestre=1)

        # ordenes
        self.orden1 = Orden.objects.create(materia=self.materia, prestatario=self.user_prestatario,
                                           lugar=Ubicacion.CAMPUS, inicio=make_aware(datetime(2024, 10, 5, 0)),
                                           final=make_aware(datetime(2024, 10, 5, 0)))

        self.orden1.agregar_corresponsable(self.user_prestatario)

        self.orden2 = Orden.objects.create(materia=self.materia, lugar=Ubicacion.EXTERNO,
                                           prestatario=self.user_prestatario,
                                           inicio=make_aware(datetime(2024, 10, 5, 0)),
                                           final=make_aware(datetime(2024, 10, 5, 0)))

        self.orden2.agregar_corresponsable(self.user_prestatario)

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

        # está suspendido
        self.assertFalse(prestatario.suspendido(), msg="El usuario ya esta suspendido")

        # un reporte
        self.orden1.reportar(almacen=almacen, descripcion="Descripcion 1")
        self.assertEqual(len(prestatario.reportes()), 1, msg="El prestatario No se ha reportado")

        # multiples reportes
        self.orden2.reportar(almacen=almacen, descripcion="Descripcion 2")
        self.assertEqual(len(prestatario.reportes()), 2, msg="El prestatario No se ha reportado varias veces")

        # está suspendido
        self.assertTrue(prestatario.suspendido(), msg="El usuario NO esta suspendido")

    def test_lista_materias(self):
        prestatario = Prestatario.get_user(self.user_prestatario)

        # nigunda materia
        self.assertEqual(len(prestatario.materias()), 0, msg="El prestatario no tiene materias")

        # agregar el usario a las materias
        materia1 = Materia.objects.create(nombre="Fotografia", year=2022, semestre=1)
        materia2 = Materia.objects.create(nombre="Edicion y diseño", year=2022, semestre=1)

        materia1.agregar_alumno(prestatario)
        materia2.agregar_alumno(prestatario)

        materias = prestatario.materias()
        self.assertIn(materia1, materias)
        self.assertIn(materia2, materias)

    def test_carrito(self):
        prestatario = Prestatario.get_user(self.user_prestatario)

        # carrito vacío
        self.assertFalse(prestatario.tiene_carrito(), msg="El usuario ya tiene un carrito")

        carrito = Carrito.objects.create(prestatario=self.user_prestatario, materia=self.materia,
                                         inicio=make_aware(datetime.now()), final=make_aware(datetime.now()))

        self.assertEqual(prestatario.carrito(), carrito, msg="El carrito no coincide")
