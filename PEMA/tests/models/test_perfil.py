from datetime import datetime
from django.test import TestCase

from django.utils.timezone import make_aware

from PEMA.models import Perfil, Prestatario


class TestPerfil(TestCase):

    def setUp(self):
        # hay un trigger que crea automáticamente el perfil

        self.username = "username"
        self.email = "name@test.com"
        self.password = "password"
        self.first_name = "John"
        self.last_name = "Doe"

        self.prestatario = Prestatario.crear_usuario(
            id=0,
            username=self.username,
            email=self.email,
            password=self.password,
            first_name=self.first_name,
            last_name=self.last_name
        )

    def test_crear_perfil(self):
        # TODO: que pasa si un usuario no tiene perfil
        perfil = Perfil.user_data(self.prestatario)
        self.assertIsNotNone(perfil)

    def test_obtener_informacion(self):
        perfil = Perfil.user_data(self.prestatario)

        self.assertEqual(perfil.nombre(), self.first_name)
        self.assertEqual(perfil.apellido(), self.last_name)
        self.assertEqual(perfil.email(), self.email)
        self.assertEqual(perfil.username(), self.username)