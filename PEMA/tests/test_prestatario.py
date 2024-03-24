from django.contrib.auth.models import User, Group
from django.test import TestCase

from PEMA.models import Prestatario
from PEMA.models import Carrito
from PEMA.models import Materia
from PEMA.models import Reporte

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

        grupos = self.user_prestatario.groups

        self.assertTrue(
            expr=grupos.filter(name='prestatarios').exists(),
            msg=f"El usuario no se encuentra en el grupo prestatarios: {grupos}"
        )


        self.assertTrue(User.objects.filter(username="sin_rol").exists())
        self.assertTrue(User.objects.filter(username="prestatario").exists())

    def self_lista_ordenes(self):
        carrito = Carrito.objects.create(
            prestatario=Prestatario.objects.get(usuario=self.user_prestatario),
            fecha=make_aware(datetime.now())
        )

        materia = Materia.objects.create(
            nombre="Fotografia",
            periodo="2024-1"
        )

        orden = Reporte.objects.create(
            carrito=carrito,
            materia=materia,
            fecha=make_aware(datetime.now())
        )

        self.assertTrue(orden in carrito.lista_ordenes())

    class TestUsers2(TestCase):
        def setUp(self):
            Prestatario.crear_grupo()

            self.user_almacen = User.objects.create_user(
                id=2,
                username="sin_rol",
                password="<PASSWORD>"
            )

            my_group = Group.objects.get(name='almacen')
            my_group.user_set.add(self.user_almacen)

        def test_lista_reportes(self):
            self.reporte = Reporte.objects.create(
                almacen=self.user_almacen,
                orden="Orden 1",
            )

            self.reporte.estado = "IN"

            self.assertEqual(self.reporte.almacen, self.user_almacen)
            self.assertEqual(self.reporte.orden, "Orden 1")
            self.assertEqual(self.reporte.estado, "IN")

    def test_lista_materias(self):
        materia1 = Materia.objects.create(
            nombre="Fotografia",
            periodo="2024-1"
        )

        materia2 = Materia.objects.create(
            nombre="Edicion y diseño",
            periodo="2024-1"
        )

        materia3 = Materia.objects.create(
            nombre="Animacion",
            periodo="2024-1"
        )

        materias = Materia.objects.all()

        self.assertIn(materia1, materias)
        self.assertIn(materia2, materias)
        self.assertIn(materia3, materias)

    def test_carrito(self):
        materia = Materia.objects.create(
            nombre="Fotografia",
            periodo="2024-1"
        )

        self.carrito = Carrito.objects.create(
            prestatario=self.user_prestatario,
            materia=materia,
            inicio=datetime.now(),
            final=datetime.now()
        )

        self.assertEqual(self.carrito.prestatario, self.user_prestatario)
        self.assertEqual(self.carrito.inicio, self.carrito.inicio)
        self.assertEqual(self.carrito.final, self.carrito.final)
        self.assertEqual(self.carrito.materia, materia)

    def test_suspendido(self):

        self.user_prestatario.is_active = False
        self.user_prestatario.save()

        self.assertFalse(self.user_prestatario.is_active)