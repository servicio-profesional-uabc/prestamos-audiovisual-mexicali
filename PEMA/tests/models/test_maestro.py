import unittest
from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils.timezone import make_aware

from PEMA.models import Materia, Orden, TipoOrden, Maestro, AutorizacionOrden
from PEMA.models import Prestatario


class TestMaestro(TestCase):
    def setUp(self):
        self.prestatario = Prestatario.objects.create(id=7, username="prestatario_prueba", password="<PASSWORD>")
        self.user_maestro = Maestro.crear_usuario(id=8, username="maestro_prueba", password="<PASSWORD>")

        self.materia = Materia.objects.create(nombre="Fotografía", year=2022, semestre=1)
        self.materia.agregar_maestro(Maestro.get_user(self.user_maestro))

        self.orden_ordinaria = Orden.objects.create(prestatario=self.prestatario, materia=self.materia,
                                          inicio=make_aware(datetime(2024, 3, 16, 12)),
                                          final=make_aware(datetime(2024, 3, 16, 18)),
                                          tipo=TipoOrden.ORDINARIA)

    def test_materias(self):
        materia1 = self.materia
        materia2 = Materia.objects.create(nombre="Cinefotografía I",  year=2022, semestre=1)
        materia3 = Materia.objects.create(nombre="Cinefotografía II",  year=2022, semestre=1)

        materias = Materia.objects.all()

        self.assertIn(materia1, materias)
        self.assertIn(materia2, materias)
        self.assertIn(materia3, materias)

    @unittest.skip("Skipping this test")
    def test_solicitar_autorizacion(self):
        self.assertEqual(AutorizacionOrden.objects.count(), 0)
        Maestro.solicitar_autorizacion(self.orden_ordinaria)
        self.assertEqual(AutorizacionOrden.objects.count(), 1)

