
from django.contrib.auth.models import User
from django.test import TestCase


from PEMA.models import Maestro
from PEMA.models import Orden


from PEMA.models import Prestatario


from datetime import datetime




class TestMaestro(TestCase):
   def setUp(self):
       self.prestatario = Prestatario.objects.create(
               id=7,
               username="prestatario_prueba",
               password="<PASSWORD>"
       )


       self.user_maestro = User.objects.create(
           id=8,
           username="maestro_prueba",
           password="<PASSWORD>"
       )


   def test_autorizar_ordinaria(self):
       orden = Orden.objects.create(
           prestatario=self.prestatario,
           tipo="ordinaria",
           lugar="",
           inicio=datetime.now(),
           final=datetime.now()
       )


       Maestro.autorizar(self.user_maestro, orden)



