from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.test import TestCase

from PEMA.models import Prestatario
from PEMA.models import Carrito

from django.utils.timezone import make_aware
from datetime import datetime


class TestUsers(TestCase):
    def setUp(self):

        Prestatario.crear_grupo()

        self.user_normal = User.objects.create_user(
            id=0,
            username="sin_rol",
            password="<PASSWORD>"
        )

        self.user_prestatario = User.objects.create(
            id=1,
            username="prestatario",
            password="<PASSWORD>"
        )

        my_group = Group.objects.get(name='prestatarios')
        my_group.user_set.add(self.user_prestatario)

        self.user_normal.save()
        self.user_prestatario.save()

    def test_crear_prestatario(self):
        # verificar que el prestatario está en el grupo prestatario

        grupos = self.user_prestatario.groups

        self.assertTrue(
            expr=grupos.filter(name='prestatarios').exists(),
            msg=f"El usuario no se encuentra en el grupo prestatarios: {grupos}"
        )


