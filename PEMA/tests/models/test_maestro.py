from django.contrib.auth.models import User
from django.test import TestCase

from PEMA.models import Materia
from PEMA.models import Prestatario


class TestMaestro(TestCase):
    def setUp(self):
        self.prestatario = Prestatario.objects.create(id=7, username="prestatario_prueba", password="<PASSWORD>")

        self.user_maestro = User.objects.create(id=8, username="maestro_prueba", password="<PASSWORD>")

    def test_materias(self):
        materia1 = Materia.objects.create(nombre="Fotografía", periodo="2024-2")
        materia2 = Materia.objects.create(nombre="Cinefotografía I", periodo="2024-2")
        materia3 = Materia.objects.create(nombre="Cinefotografía II", periodo="2024-2")

        materias = Materia.objects.all()

        self.assertIn(materia1, materias)
        self.assertIn(materia2, materias)
        self.assertIn(materia3, materias)
