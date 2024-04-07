from django.contrib.auth.models import User, Group
from django.test import TestCase

from PEMA.models import Materia, Prestatario, Coordinador, Almacen, Maestro, ArticuloMateria, Articulo


class MateriaTestCase(TestCase):

    def setUp(self):
        self.materia = Materia.objects.create(nombre="Fotografia", periodo="2024-1")
        self.user_prestatario = Prestatario.crear_usuario(id=0, username="prestatario_prueba", password="<PASSWORD>")
        self.user_coordinador = Coordinador.crear_usuario(id=1, username="coordinador_prueba", password="<PASSWORD>")
        self.user_almacen = Almacen.crear_usuario(id=2, username="almacen_prueba", password="<PASSWORD>")
        self.user_maestro = Maestro.crear_usuario(id=3, username="maestro_prueba", password="<PASSWORD>")

    def test_crear_materia(self):
        self.assertEqual(self.materia.nombre, "Fotografia")
        self.assertEqual(self.materia.periodo, "2024-1")

    def test_metodo_alumnos(self):
        # alumno unico
        self.materia.agregar_alumno(self.user_prestatario)
        self.assertIn(self.user_prestatario, self.materia.alumnos(), msg="No se agrego al profesor")

        # agregar otro alumno
        alumno_dos = Prestatario.crear_usuario(id=99, username="alumno2", password="<PASSWORD>")
        self.materia.agregar_alumno(alumno_dos)

        # ambos están en la clase
        lista_alumnos_actualizada = self.materia.alumnos()
        self.assertIn(self.user_prestatario, lista_alumnos_actualizada, msg="El profesor 1 ha sido eliminado")
        self.assertIn(alumno_dos, lista_alumnos_actualizada, msg="El profesor 2 ha sido eliminado")

    def test_metodo_profesores(self):
        # maestro unico
        self.materia.agregar_maestro(self.user_maestro)
        self.assertIn(self.user_maestro, self.materia.maestros(), msg="No se agrego al profesor")

        # agregar otro maestro
        maestro_dos = Maestro.crear_usuario(id=99, username="maestro2", password="<PASSWORD>")
        self.materia.agregar_maestro(maestro_dos)

        # verificar si ambos estan en el query set
        lista_maestros_actualizada = self.materia.maestros()
        self.assertIn(self.user_maestro, lista_maestros_actualizada, msg="El profesor 1 ha sido eliminado")
        self.assertIn(maestro_dos, lista_maestros_actualizada, msg="El profesor 2 ha sido eliminado")

    def test_metodo_articulos(self):
        # TODO: rehacer esta pruebas
        articulo1 = Articulo.objects.create(nombre="Camara Canon", codigo="123",
                                            descripcion="Camara de alta definicion - hdr")

        articulo2 = Articulo.objects.create(nombre="Camara Blackmagic", codigo="124",
                                            descripcion="Camara de alta definicion - hdr - blackmagic")

        ArticuloMateria.objects.get_or_create(materia=self.materia, articulo=articulo1)

        ArticuloMateria.objects.get_or_create(materia=self.materia, articulo=articulo2)

        # Ejemplo: Comparte articulo1 con materia1
        materia2 = Materia.objects.create(nombre="Video", periodo="2024-1", )

        ArticuloMateria.objects.get_or_create(materia=materia2, articulo=articulo1, )

        # No tiene articulos
        materia3 = Materia.objects.create(nombre="Guion", periodo="2024-1", )

        materia_articulos = self.materia.articulos()
        materia_articulos_esperadas = Articulo.objects.filter(articulomateria__materia=self.materia)

        for a in materia_articulos:
            self.assertIn(a, materia_articulos_esperadas)

        materia_articulos = materia2.articulos()
        materia_articulos_esperadas = Articulo.objects.filter(articulomateria__materia=materia2)
        for a in materia_articulos:
            self.assertIn(a, materia_articulos_esperadas)

        self.assertNotIn(articulo2, materia2.articulos())

        self.assertNotEqual(materia3.articulos(), None)
