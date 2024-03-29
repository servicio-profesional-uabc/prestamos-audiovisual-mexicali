from datetime import datetime

from django.contrib.auth.models import User, Group
from django.test import TestCase
from django.utils.timezone import make_aware

from PEMA.models import Prestatario, Materia, Carrito, Articulo, Orden


class TestCarrito(TestCase):
    def setUp(self):
        # crear usuario Prestatario
        # -----
        Prestatario.crear_grupo()
        grupo_prestatario = Group.objects.get(name='prestatarios')

        self.user = User.objects.create_user(
            id=0,
            username="<USERNAME>",
            password="<PASSWORD>"
        )

        self.user.groups.add(grupo_prestatario)

        # crear materia
        # -----
        self.materia = Materia.objects.create(
            nombre="<MATERIA>",
            periodo="2024-1",
        )

        # crear articulo
        # -----
        self.articulo = Articulo.objects.create(
            nombre="<ARTICULO>",
            codigo="0000-0000",
        )

        # crear carrito
        # -----
        self.carrito = Carrito.objects.create(
            prestatario=self.user,
            materia=self.materia,
            inicio=make_aware(datetime(2024, 3, 16, 12)),
            final=make_aware(datetime(2024, 3, 16, 18)),
        )

    def test_agregar(self):
        self.assertEquals(
            len(self.carrito.articulos()),
            0,
            msg="El Carrito No está vació"
        )

        self.carrito.agregar(
            articulo=self.articulo
        )

        self.assertEquals(
            len(self.carrito.articulos()),
            1,
            msg="No se agrego ningún articulo"
        )

        # volver a agregar
        self.carrito.agregar(
            articulo=self.articulo
        )

        self.assertEquals(
            len(self.carrito.articulos()),
            1,
            msg="Se duplicaron artículos"
        )

    def test_actualizar_unidades(self):
        foo, _ = self.carrito.agregar(
            articulo=self.articulo
        )

        prev = foo.unidades

        bar, _ = self.carrito.agregar(
            articulo=self.articulo,
            unidades=3
        )

        post = bar.unidades

        self.assertNotEquals(
            prev,
            post,
            msg="No se actualizó la cantidad de unidades"
        )

    def test_ordenar(self):
        self.carrito.ordenar()

        self.assertEquals(
            len(Carrito.objects.all()),
            0,
            msg="No se Eliminó el Carrito"
        )

        self.assertEquals(
            len(Orden.objects.all()),
            1,
            msg="No se creo la Orden"
        )
