import datetime

from django.contrib.auth.models import User, Group
from django.test import TestCase

from PEMA.models import Almacen, Orden, Prestatario


class TestCaseAlmacen(TestCase):
    def test_crear_orden(self):
        Prestatario.crear_grupo()
        Almacen.crear_grupo()

        user_almacen = User.objects.create(
            id=0,
            username="almacen_prueba",
            password="<PASSWORD>"
        )

        user_prestatario = User.objects.create(
            id=21,
            username="prestatario_prueba",
            password="<PASSWORD>"
        )

        my_group = Group.objects.get(name='almacen')
        my_group.user_set.add(user_almacen)

        my_group = Group.objects.get(name='prestatarios')
        my_group.user_set.add(user_prestatario)

        orden = Orden.objects.create(
            prestatario=user_prestatario,
            lugar='Un lugar',
            inicio=datetime.datetime.now(datetime.timezone.utc),
            final=datetime.datetime.now(datetime.timezone.utc),
        )

        self.assertEqual(orden.prestatario, user_prestatario)
        self.assertEqual(orden.estado_atr, 'PN')
        self.assertEqual(orden.tipo, 'OR')
        self.assertEqual(orden.lugar, 'Un lugar')