from django.test import TestCase
from django.utils import timezone

from PEMA.models import Orden, Prestatario, CorresponsableOrden, Materia


class TestCorresponsableOrden(TestCase):
    def setUp(self):
        self.user = Prestatario.crear_usuario(username='testuser', email='test@example.com')
        self.materia = Materia.objects.create(nombre='test', year=10, semestre=2)
        self.orden = Orden.objects.create(materia=self.materia,prestatario=self.user, inicio=timezone.now(), final=timezone.now())

    def test_orden_updated_signal(self):
        # no hay coppesponsables
        self.assertEqual(CorresponsableOrden.objects.all().count(), 0)

        # crear CorresponsableOrden cada vez que se agrega un corresponsable
        self.orden.agregar_corresponsable(self.user)
        self.assertEqual(CorresponsableOrden.objects.all().count(), 1)

        # eliminar Corresponsable cada vez que se elimina un corresponsable
        self.orden.corresponsables().delete()
        self.assertEqual(CorresponsableOrden.objects.all().count(), 0)

