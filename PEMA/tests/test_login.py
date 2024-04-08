from django.test import TestCase, Client
from django.urls import reverse
from PEMA.models import User
from PEMA.forms import UserLoginForm

class TestLogin(TestCase):

    MATRICULA = '1234567'
    EMAIL = '<EMAIL>'
    PASSWORD = 'P@ssword123'

    def setUp(self):
        self.user = User.objects.create(
            username=self.MATRICULA,
            email=self.EMAIL,
        )
        self.user.set_password(self.PASSWORD) # set password hashea

    def test_login_success_view(self):
        # Instancear form UserLoginForm
        form = UserLoginForm()
        form.username = self.MATRICULA
        form.password = self.PASSWORD

        # Inicializar cliente
        client = Client()

        # Definir URL para la vista login
        url = reverse('login') # ruta real es '', tuve que poner login porque reverse no acepta '', pero es lo mismo

        # Enviar solicitudes POST con datos del form
        response = client.post(url, {'username': form.username, 'password' : form.password})

        # Revisar si el usuario haya realizado el login satisfactoriamente
        self.assertEqual(response.status_code, 200)

    def test_login_error_view(self):
        client = Client()

        url = reverse('login')

        form = UserLoginForm()
        self.MATRICULA = 'ASDOASJD'
        form.username = self.MATRICULA
        form.password = self.PASSWORD

        response = client.post(url, {'username':form.username, 'password':form.password})

        self.assertEqual(response.status_code, 200)
        self.assertInHTML('<div class="alert alert-danger mt-2 small" role="alert"> El nombre de usuario o la contraseña que escribió son incorrectos. Inténtelo nuevamente. Si aún no puede iniciar sesión, comuníquese con el administrador del sistema.</div>', response.content.decode())

        self.MATRICULA = '1234567'
        form.username = self.MATRICULA
        self.PASSWORD = 'P@3333as'
        form.password = self.PASSWORD

        response = client.post(url, {'username':form.username, 'password':form.password})

        self.assertEqual(response.status_code, 200)
        self.assertInHTML('<div class="alert alert-danger mt-2 small" role="alert"> El nombre de usuario o la contraseña que escribió son incorrectos. Inténtelo nuevamente. Si aún no puede iniciar sesión, comuníquese con el administrador del sistema.</div>', response.content.decode())
