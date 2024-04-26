from datetime import datetime

from django.test import TestCase
from django.utils.timezone import make_aware

from PEMA.models import Articulo
from PEMA.models import Materia
from PEMA.models import Categoria
from PEMA.models import Orden
from PEMA.models import Prestatario


class TestArticulo(TestCase):

    @staticmethod
    def generar_fechas(hora):
        return make_aware(datetime(2024, 3, 16, 12 + hora))

    def setUp(self):
        self.user = Prestatario.crear_usuario(
            id=0,
            username="sin_rol",
            password="<PASSWORD>"
        )

        self.articulo = Articulo.objects.create(
            nombre="articulo 1",
            codigo="codigo 1"
        )

        self.unidad, _ = self.articulo.crear_unidad(
            num_control="num_control 1",
            num_serie="num_series 2"
        )

        self.materia = Materia.objects.create(nombre="fotografia", year=2022, semestre=1)

        self.orden_antes = Orden.objects.create(
            materia=self.materia,
            prestatario=self.user,
            lugar="Prueba antes",
            inicio=self.generar_fechas(-1),
            final=self.generar_fechas(1)
        )

        self.orden_despues = Orden.objects.create(
            materia=self.materia,
            prestatario=self.user,
            lugar="prueba despues",
            inicio=self.generar_fechas(0),
            final=self.generar_fechas(1)
        )

        self.orden_antes.agregar_unidad(unidad=self.unidad)
        self.orden_despues.agregar_unidad(unidad=self.unidad)

        self.materia1 = Materia.objects.create(nombre='Cinematografia', year=2024, semestre=1)
        
        self.articulo1 = Articulo.objects.create(nombre="C1", codigo="123")
        
        self.articulo2 = Articulo.objects.create(nombre="C2", codigo="111")
        

        
        self.unidad1, created = self.articulo1.crear_unidad(
            num_control="1", num_serie="1"
        )
        self.unidad2, created = self.articulo1.crear_unidad(
            num_control="2", num_serie="2"
        )
        self.unidad3, created = self.articulo1.crear_unidad(
            num_control="3", num_serie="3"
        )
        self.unidad4, created = self.articulo1.crear_unidad(
            num_control="4", num_serie="4"
        )
        self.unidad5, created = self.articulo2.crear_unidad(
            num_control="5", num_serie="5"
        )
        self.unidad6, created = self.articulo2.crear_unidad(
            num_control="6", num_serie="6"
        )
        self.unidad7, created = self.articulo2.crear_unidad(
            num_control="7", num_serie="7"
        )
        self.unidad8, created = self.articulo2.crear_unidad(
            num_control="8", num_serie="8"
        )
        
        self.materia1.agregar_articulo(self.articulo1)
        self.materia1.agregar_articulo(self.articulo2)
        
        self.orden1 = Orden.objects.create(
            materia=self.materia1,
            prestatario=self.user,
            lugar="orden 12:00 a 14:00",
            estado="PA",
            inicio=self.generar_fechas(0),
            final=self.generar_fechas(2)
        )
        self.orden2 = Orden.objects.create(
            materia=self.materia1,
            prestatario=self.user,
            lugar="orden 11:00 a 14:00",
            estado="PC",
            inicio=self.generar_fechas(-1),
            final=self.generar_fechas(2)
        )
        self.orden3 = Orden.objects.create(
            materia=self.materia1,
            prestatario=self.user,
            lugar="orden 15:00 a 17:00",
            estado="AP",
            inicio=self.generar_fechas(3),
            final=self.generar_fechas(5)
        )
        self.orden4 = Orden.objects.create(
            materia=self.materia1,
            prestatario=self.user,
            lugar="orden 16:00 a 18:00",
            estado="PA",
            inicio=self.generar_fechas(4),
            final=self.generar_fechas(6)
        )
        self.orden5 = Orden.objects.create(
            materia=self.materia1,
            prestatario=self.user,
            lugar="orden 13:00 a 16:00",
            estado="PC",
            inicio=self.generar_fechas(1),
            final=self.generar_fechas(4)
        )
        self.orden6 = Orden.objects.create(
            materia=self.materia1,
            prestatario=self.user,
            lugar="orden 11:00 a 18:00",
            estado="AP",
            inicio=self.generar_fechas(-1),
            final=self.generar_fechas(6)
        )
        
    def test_unidades(self):
        unidades = self.articulo.unidades()

        self.assertIn(self.unidad, unidades, "Unidades no registradas de manera correcta")
        self.assertEqual(len(unidades), 1, "Unidades no registradas")

    def test_categorias(self):
        # crear categorías
        categoria1 = Categoria.objects.create(nombre="Categoría 1")
        categoria2 = Categoria.objects.create(nombre="Categoría 2")

        # agregar el artículo
        categoria1.agregar(self.articulo)
        categoria2.agregar(self.articulo)

        # test
        categorias_articulo = self.articulo.categorias()

        self.assertIn(categoria1, categorias_articulo, msg="La categoría no se agrego correctamente")
        self.assertEqual(len(categorias_articulo), 2, msg="Numero incorrecto de categorías")

    def test_materia(self):
        self.materia.agregar_articulo(self.articulo)

        self.assertIn(self.materia, self.articulo.materias())
        
    def test_disponible(self):
        
        self.orden1.agregar_unidad(self.unidad1)        
        self.orden2.agregar_unidad(self.unidad2)
        self.orden3.agregar_unidad(self.unidad3)
        self.orden4.agregar_unidad(self.unidad4)
        self.orden5.agregar_unidad(self.unidad5)
        self.orden6.agregar_unidad(self.unidad6)
        
        qs1 = self.articulo1.disponible(self.generar_fechas(0), self.generar_fechas(5))
        self.assertQuerysetEqual(qs1, [], ordered=False)
        
        qs2 = self.articulo2.disponible(self.generar_fechas(0), self.generar_fechas(5))
        self.assertQuerysetEqual(qs2, [self.unidad7, self.unidad8], ordered=False)
        
        qs3 = self.articulo1.disponible(self.generar_fechas(-1), self.generar_fechas(2))
        self.assertQuerysetEqual(qs3, [self.unidad3, self.unidad4], ordered=False)
        
        qs4 = self.articulo2.disponible(self.generar_fechas(-1), self.generar_fechas(1))
        self.assertQuerysetEqual(qs4, [self.unidad5, self.unidad7, self.unidad8], ordered=False)
        
        qs5 = self.articulo1.disponible(self.generar_fechas(2), self.generar_fechas(4))
        self.assertQuerysetEqual(qs5, [self.unidad1, self.unidad2, self.unidad4], ordered=False)
        
        qs6 = self.articulo2.disponible(self.generar_fechas(1), self.generar_fechas(4))
        self.assertQuerysetEqual(qs6, [self.unidad7, self.unidad8], ordered=False)
        