from django.contrib.auth.models import User, Group
from django.test import TestCase

from PEMA.models import Prestatario

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

    def test_crear_prestatario(self):
        # verificar que el prestatario está en el grupo prestatario

        grupos = self.user_prestatario.groups

        self.assertTrue(
            expr=grupos.filter(name='prestatarios').exists(),
            msg=f"El usuario no se encuentra en el grupo prestatarios: {grupos}"
        )


