from django.test import TestCase
from PEMA.models import Categoria, Articulo


class TestCategoria(TestCase):

    CATEGORIA_NOMBRE = '<CATEGORIA>'
    ARTICULO_NOMBRE = '<ARTICULO>'
    ARTICULO_CODIGO = '<CODIGO>'
    ARTICULO_DESCRIPCION = '<DESCRIPCION>'

    def setUp(self):
        self.categoria = Categoria.objects.create(
            nombre=self.CATEGORIA_NOMBRE
        )

        self.articulo = Articulo.objects.create(
            nombre=self.ARTICULO_NOMBRE,
            codigo=self.ARTICULO_CODIGO,
            descripcion=self.ARTICULO_DESCRIPCION,
        )

    def test_agregar(self):
        # agregar por primera vez
        _, creado = self.categoria.agregar(
            articulo=self.articulo
        )

        self.assertTrue(expr=creado, msg="El articulo ya existe en la categoría")

        # agregar repetido
        _, creado = self.categoria.agregar(
            articulo=self.articulo
        )

        self.assertFalse(expr=creado, msg="El articulo NO existe en la categoría")

    def test_lista_articulos(self):

        _, creado = self.categoria.agregar(
            articulo=self.articulo
        )

        self.assertEquals(
            self.categoria.articulos()[0].nombre,
            self.ARTICULO_NOMBRE,
            msg="El articulo no existe pertenece a la Categoría"
        )
