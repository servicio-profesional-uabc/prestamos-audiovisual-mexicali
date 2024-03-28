from datetime import datetime
from django.test import TestCase

from django.utils.timezone import make_aware

from PEMA.models import Perfil, Prestatario


class TestPerfil(TestCase):
    def setUp(self):
        # hay un trigger que crea automaticasmente el perfil
        self.prestatario = Prestatario.crear_usuario(id=0, username="<NAME>", password="<PASSWORD>")

    def test_crear_perfil(self):
        perfil, creado = Perfil.user_data(self.prestatario)
        self.assertFalse(creado, msg="El Usuario No tiene perfil")
