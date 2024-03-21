from django.contrib.auth.models import User, Group
from django.test import TestCase

from PEMA.models import Materia, Prestatario, Coordinador, Almacen, Maestro, ArticuloMateria, Articulo


class MateriaTestCase(TestCase):
    def test_crear_materia(self):
        self.materia = Materia.objects.create(
            nombre="Fotografia",
            periodo="2024-1"
        )

        self.assertEqual(self.materia.nombre, "Fotografia")
        self.assertEqual(self.materia.periodo, "2024-1")

    def test_metodo_alumnos(self):
        Prestatario.crear_grupo()
        Coordinador.crear_grupo()
        Almacen.crear_grupo()
        Maestro.crear_grupo()

        self.user_prestatario = User.objects.create(
            id=0,
            username="prestatario_prueba",
            password="<PASSWORD>"
        )

        self.user_coordinador = User.objects.create(
            id=1,
            username="coordinador_prueba",
            password="<PASSWORD>"
        )

        self.user_almacen = User.objects.create(
            id=2,
            username="almacen_prueba",
            password="<PASSWORD>"
        )

        self.user_maestro = User.objects.create(
            id=3,
            username="maestro_prueba",
            password="<PASSWORD>"
        )

        my_group = Group.objects.get(name='prestatarios')
        my_group.user_set.add(self.user_prestatario)

        my_group = Group.objects.get(name='coordinador')
        my_group.user_set.add(self.user_coordinador)

        my_group = Group.objects.get(name='almacen')
        my_group.user_set.add(self.user_almacen)

        my_group = Group.objects.get(name='maestro')
        my_group.user_set.add(self.user_maestro)

        self.user_prestatario.save()
        self.user_almacen.save()
        self.user_coordinador.save()
        self.user_maestro.save()

        materia = Materia.objects.create(
            nombre="Fotografia",
            periodo="2024-1"
        )

        respuesta = User.objects.exclude(groups__name__in=['coordinador', 'almacen', 'maestro'])

        self.assertQuerysetEqual(materia.alumnos(), respuesta)

    def test_metodo_profesores(self):
        Prestatario.crear_grupo()
        Coordinador.crear_grupo()
        Almacen.crear_grupo()
        Maestro.crear_grupo()

        self.user_prestatario = User.objects.create(
            id=0,
            username="prestatario_prueba",
            password="<PASSWORD>"
        )

        self.user_coordinador = User.objects.create(
            id=1,
            username="coordinador_prueba",
            password="<PASSWORD>"
        )

        self.user_almacen = User.objects.create(
            id=2,
            username="almacen_prueba",
            password="<PASSWORD>"
        )

        self.user_maestro = User.objects.create(
            id=3,
            username="maestro_prueba",
            password="<PASSWORD>"
        )

        my_group = Group.objects.get(name='prestatarios')
        my_group.user_set.add(self.user_prestatario)

        my_group = Group.objects.get(name='coordinador')
        my_group.user_set.add(self.user_coordinador)

        my_group = Group.objects.get(name='almacen')
        my_group.user_set.add(self.user_almacen)

        my_group = Group.objects.get(name='maestro')
        my_group.user_set.add(self.user_maestro)

        self.user_prestatario.save()
        self.user_almacen.save()
        self.user_coordinador.save()
        self.user_maestro.save()

        materia = Materia.objects.create(
            nombre="Fotografia",
            periodo="2024-1"
        )

        respuesta = User.objects.exclude(groups__name__in=['coordinador', 'almacen', 'prestatarios'])

        self.assertQuerysetEqual(materia.profesores(), respuesta)

    def test_metodo_articulos(self):
        materia = Materia.objects.create(
            nombre="Fotografia",
            periodo="2024-1"
        )

        articulo1 = Articulo.objects.create(
            nombre="Camara Canon",
            codigo="123",
            descripcion="Camara de alta definicion - hdr"
        )

        articulo2 = Articulo.objects.create(
            nombre="Camara Blackmagic",
            codigo="124",
            descripcion="Camara de alta definicion - hdr - blackmagic"
        )

        ArticuloMateria.objects.get_or_create(
            materia=materia,
            articulo=articulo1
        )

        ArticuloMateria.objects.get_or_create(
            materia=materia,
            articulo=articulo2
        )

        # Ejemplo: Comparte articulo1 con materia1
        materia2 = Materia.objects.create(
            nombre="Video",
            periodo="2024-1",
        )

        ArticuloMateria.objects.get_or_create(
            materia=materia2,
            articulo=articulo1,
        )

        # No tiene articulos
        materia3 = Materia.objects.create(
            nombre="Guion",
            periodo="2024-1",
        )

        materia_articulos = materia.articulos()
        materia_articulos_esperadas = Articulo.objects.filter(articulomateria__materia=materia)

        for a in materia_articulos:
            self.assertIn(a, materia_articulos_esperadas)

        materia_articulos = materia2.articulos()
        materia_articulos_esperadas = Articulo.objects.filter(articulomateria__materia=materia2)
        for a in materia_articulos:
            self.assertIn(a, materia_articulos_esperadas)

        self.assertNotIn(articulo2, materia2.articulos())

        self.assertNotEqual(materia3.articulos(), None)
