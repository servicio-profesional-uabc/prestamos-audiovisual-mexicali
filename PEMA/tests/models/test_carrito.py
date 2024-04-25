import unittest
from datetime import datetime
from unittest import skip

from django.contrib.auth.models import User, Group
from django.test import TestCase
from django.utils.timezone import make_aware

from PEMA.models import Prestatario, Materia, Carrito, Articulo, Orden, CorresponsableOrden


class TestCarrito(TestCase):
    def setUp(self):
        # crear usuario Prestatario
        Prestatario.crear_grupo()
        grupo_prestatario = Group.objects.get(name='prestatarios')

        self.user = Prestatario.crear_usuario(id=0, username="<USERNAME>", password="<PASSWORD>")

        self.user.groups.add(grupo_prestatario)

        # crear materia
        self.materia = Materia.objects.create(nombre="fotografia", year=2022, semestre=1)

        # crear articulo
        self.articulo = Articulo.objects.create(nombre="<ARTICULO>", codigo="0000-0000", )

        # crear carrito
        self.carrito = Carrito.objects.create(prestatario=self.user, materia=self.materia,
                                              inicio=make_aware(datetime(2024, 3, 16, 12)),
                                              final=make_aware(datetime(2024, 3, 16, 18)), )

    def test_agregar(self):
        # carrito vacío
        self.assertEquals(len(self.carrito.articulos_carrito()), 0, msg="El Carrito No está vació")

        # carrito con un articulo agregado
        self.carrito.agregar(articulo=self.articulo, unidades=1)
        self.assertEquals(len(self.carrito.articulos_carrito()), 1, msg="No se agrego ningún articulo")

        # volver a agregar el mismo articulo
        self.carrito.agregar(articulo=self.articulo, unidades=1)
        self.assertEquals(len(self.carrito.articulos_carrito()), 1, msg="Se duplicaron artículos")

    @skip("Falta implementar los test de Ordenar carrito")
    def test_ordenar_articulo(self):
        pass

    def test_actualizar_unidades(self):
        self.carrito.agregar(articulo=self.articulo, unidades=1)
        self.carrito.agregar(articulo=self.articulo, unidades=3)

        a = self.carrito._articulos.filter(articulo=self.articulo)

        self.assertEquals(len(a), 1, msg="Cantidad incorrecta de elementos")
        self.assertEquals(a.first().unidades, 3, msg="No se actualizó la cantidad de unidades")

    def test_ordenar(self):
        self.carrito.ordenar()

        self.assertEquals(len(Carrito.objects.all()), 0, msg="No se Eliminó el Carrito")
        self.assertEquals(len(Orden.objects.all()), 1, msg="No se creo la Orden")
        self.assertEquals(len(CorresponsableOrden.objects.all()), 1, msg="La orden NO tiene corresponsable")
