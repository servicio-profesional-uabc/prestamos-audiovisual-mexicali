import datetime

from django.test import TestCase
from django.utils.timezone import make_aware

from PEMA.models import Almacen, Orden, Prestatario, Materia


class TestCaseAlmacen(TestCase):
    def setUp(self):
        # crear usuarios
        self.almacen = Almacen.crear_usuario(id=0, username="almacen_prueba", password="<PASSWORD>")
        self.prestatario = Prestatario.crear_usuario(id=21, username="prestatario_prueba", password="<PASSWORD>")

        # crear materias
        self.materia1 = Materia.objects.create(nombre="materia", year=2022, semestre=1)
        self.materia2 = Materia.objects.create(nombre="fotografia", year=2022, semestre=1)

        # crear orden
        now = make_aware(datetime.datetime.now())
        self.orden1 = Orden.objects.create(prestatario=self.prestatario, materia=self.materia1, inicio=now, final=now, )
        self.orden2 = Orden.objects.create(prestatario=self.prestatario, materia=self.materia2, inicio=now, final=now, )

    def test_get_users(self):
        # obtener usuarios
        usuario_almacen = Almacen.get_user(self.almacen)
        self.assertEqual(usuario_almacen, self.almacen, msg="Usuario NO es almacen")

    def test_get_user_no_almacen(self):
        usuario_no_almacen = Almacen.get_user(self.prestatario)
        self.assertIsNone(usuario_no_almacen, msg="Usuario es almacen")
