from datetime import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import make_aware

from PEMA.models import Orden, EstadoOrden
from PEMA.models import Prestatario, Materia


class DetallesOrdenViewTestCase(TestCase):
    USERNAME = '1234567'
    PASSWORD = 'password'

    def setUp(self):
        self.user = Prestatario.crear_usuario(username=self.USERNAME, password=self.PASSWORD)

        self.materia = Materia.objects.create(nombre='Cinematografia', year=2022, semestre=1)

        self.orden = Orden.objects.create(prestatario=self.user, nombre="Lorem ipsum dolor sit amet",
                                          lugar=Orden.Ubicacion.CAMPUS, inicio=make_aware(datetime(2024, 10, 5)),
                                          final=make_aware(datetime(2024, 10, 5)), estado=EstadoOrden.PENDIENTE_AP,
                                          materia=self.materia, )

    def test_get_detalles_orden(self):
        self.client.login(username=self.USERNAME, password=self.PASSWORD)

        # GET request para la vista detalles_orden de la orden especifica
        response = self.client.get(reverse('detalles_orden', kwargs={'id': self.orden.id}))

        # Checar si se carga exitosamente la pagina
        self.assertEqual(response.status_code, 200)

        # Checar si los detalles de la orden estan presentes en la respuesta
        self.assertEqual(response.context['orden'], self.orden)

    def test_post_cancelar_orden(self):
        self.client.login(username=self.USERNAME, password=self.PASSWORD)

        response = self.client.post(reverse('detalles_orden', kwargs={'id': self.orden.id}))

        self.orden.refresh_from_db()  # Refrescar instancia de orden en la base de datos
        self.assertEqual(self.orden.estado, EstadoOrden.CANCELADA)

        # Checar si el usuario se redirige a historial_solicitudes despues de cancelar
        self.assertRedirects(response, reverse('historial_solicitudes'))
