from django.test import TestCase

from PEMA.models import Materia, Prestatario, Coordinador, Almacen, Maestro, Articulo


class MateriaTestCase(TestCase):

    def setUp(self):
        self.materia = Materia.objects.create(nombre="Fotografia", year=2022, semestre=1)

        self.user_prestatario = Prestatario.crear_usuario(id=0, username="prestatario_prueba", password="<PASSWORD>")
        self.user_coordinador = Coordinador.crear_usuario(id=1, username="coordinador_prueba", password="<PASSWORD>")
        self.user_almacen = Almacen.crear_usuario(id=2, username="almacen_prueba", password="<PASSWORD>")
        self.user_maestro = Maestro.crear_usuario(id=3, username="maestro_prueba", password="<PASSWORD>")

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
        # articulos para la lista
        articulo1 = Articulo.objects.create(nombre="Camara Canon", codigo="123")
        articulo2 = Articulo.objects.create(nombre="Camara Blackmagic", codigo="124")

        # agregar articulos
        self.materia.agregar_articulo(articulo1)
        self.materia.agregar_articulo(articulo2)

        lista_articulos = self.materia.articulos()
        self.assertIn(articulo1, lista_articulos, msg="NO se agrego al articulo 1")
        self.assertIn(articulo2, lista_articulos, msg="NO se agrego al articulo 2")
