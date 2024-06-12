from datetime import datetime

from django.test import TestCase
from django.utils.timezone import make_aware

from PEMA.models import Prestatario, Articulo, Orden, Reporte, Almacen, Materia, Ubicacion, EstadoOrden, AutorizacionEstado, \
    CorresponsableOrden, TipoOrden


class TestOrden(TestCase):
    @staticmethod
    def generar_fechas(hora):
        return make_aware(datetime(2024, 5, 24, 12 + hora))
    
    def setUp(self):
        # usuarios
        self.prestataio = Prestatario.crear_usuario(id=0, username="<NAME>", password="<PASSWORD>")
        self.almacen = Almacen.crear_usuario(id=1, username="<NAME2>", password="<PASSWORD>")

        # crear artículos
        self.articulo1 = Articulo.objects.create(nombre="Articulo 1", codigo="100")
        self.articulo2 = Articulo.objects.create(nombre="Articulo 2", codigo="200")

        # crear unidades
        self.unidad1, _ = self.articulo1.crear_unidad(num_control="000", num_serie="000")
        self.unidad2, _ = self.articulo2.crear_unidad(num_control="100", num_serie="200")

        materia = Materia.objects.create(nombre="Fotografia", year=2022, semestre=1)

        self.orden_ordinaria = Orden.objects.create(prestatario=self.prestataio, materia=materia,
                                                    inicio=self.generar_fechas(0),
                                                    final=self.generar_fechas(6),
                                                    tipo=TipoOrden.ORDINARIA)

        self.orden_extraordinaria = Orden.objects.create(prestatario=self.prestataio, materia=materia,
                                                         inicio=self.generar_fechas(0),
                                                         final=self.generar_fechas(6),
                                                         tipo=TipoOrden.EXTRAORDINARIA)

    def test_agregar_unidad(self):
        self.orden_ordinaria.agregar_unidad(self.unidad1)

        self.assertIn(self.unidad1, self.orden_ordinaria.unidades())

    def test_unidades(self):
        self.orden_ordinaria.agregar_unidad(self.unidad1)

        self.assertIn(member=self.unidad1, container=self.orden_ordinaria.unidades(), msg="Unidad No registrada")

    def test_articulo(self):
        # agregar el objeto de manera repetida
        self.orden_ordinaria.agregar_unidad(self.unidad1)
        self.orden_ordinaria.agregar_unidad(self.unidad1)

        self.assertEqual(len(self.orden_ordinaria.articulos()), 1, msg="Hay mas articulos registrados")

        # agregar un objeto nuevo
        self.orden_ordinaria.agregar_unidad(self.unidad2)
        self.assertEqual(len(self.orden_ordinaria.articulos()), 2, msg="Hay menos articulos registrados")

        self.assertIn(member=self.articulo1, container=self.orden_ordinaria.articulos(),
                      msg="Articulo1 No existe en la orden")
        self.assertIn(member=self.articulo2, container=self.orden_ordinaria.articulos(),
                      msg="Articulo2 No existe en la orden")

    def test_reporte(self):
        almacen = Almacen.get_user(self.almacen)

        # Si no hay reporte
        self.assertIsNone(self.orden_ordinaria.reporte(), msg="Ya existe un reporte")

        # si hay un reporte
        self.orden_ordinaria.reportar(almacen=almacen, descripcion="Nada")
        self.assertIsNotNone(obj=self.orden_ordinaria.reporte(), msg="No existe un reporte")

        # verificar que una orden no se puede reportar 2 veces
        self.orden_ordinaria.reportar(almacen=almacen, descripcion="Nada")
        self.assertEqual(len(Reporte.objects.filter(orden=self.orden_ordinaria)), 1)

    def test_entregada(self):
        # La orden no está marcada como entregada inicialmente
        self.assertFalse(self.orden_ordinaria.entregada())

        self.orden_ordinaria.estado = EstadoOrden.APROBADA
        # Marcar la orden como entregada
        self.orden_ordinaria.entregar(entregador=self.almacen)
        self.assertTrue(self.orden_ordinaria.entregada())

    def test_rechazar(self):
        self.assertFalse(self.orden_ordinaria.cancelada())
        self.orden_ordinaria.cancelar()
        self.assertTrue(self.orden_ordinaria.cancelada())

    def test_entregar(self):
        # La orden no está marcada como entregada inicialmente
        self.assertFalse(self.orden_ordinaria.entregada())

        self.orden_ordinaria.estado = EstadoOrden.APROBADA
        # Marcar la orden como entregada
        self.orden_ordinaria.entregar(entregador=self.almacen)

        # Verificar que la orden ha sido marcada como entregada
        self.assertEqual(self.orden_ordinaria.estado, EstadoOrden.ENTREGADA)

    def test_estado_corresponsables(self):
        # definir usuarios
        prest1 = Prestatario.crear_usuario("P1", "password")
        prest2 = Prestatario.crear_usuario("P2", "password")

        self.orden_ordinaria.agregar_corresponsable(prest2)
        self.orden_ordinaria.agregar_corresponsable(prest1)

        autorizaciones_corresponsables = CorresponsableOrden.objects.all()

        # CorresponsableOrden
        self.assertEqual(autorizaciones_corresponsables.count(), 2)

        # default
        self.assertEqual(self.orden_ordinaria.estado_corresponsables(), AutorizacionEstado.PENDIENTE)

        # uno rechaza
        cualquiera = autorizaciones_corresponsables.first()
        cualquiera.estado = AutorizacionEstado.RECHAZADA
        cualquiera.save()

        self.assertEqual(self.orden_ordinaria.estado_corresponsables(), AutorizacionEstado.RECHAZADA)

        # todos autorizan
        autorizaciones_corresponsables.update(estado=AutorizacionEstado.ACEPTADA)
        self.assertEqual(self.orden_ordinaria.estado_corresponsables(), AutorizacionEstado.ACEPTADA)

        # autorizaciones_corresponsables.update(estado=AutorizacionEstado.ACEPTADA)

    def test_asignar_tipo(self):
        self.prestatario = Prestatario.crear_usuario(id="123", username="test", password="<PASSWORD>")
        self.materia1 = Materia.objects.create(nombre='Cinematografia', year=2024, semestre=1)
        self.orden1 = Orden.objects.create(materia=self.materia1, prestatario=self.prestatario,
                                           lugar=Ubicacion.CAMPUS, estado=EstadoOrden.RESERVADA,
                                           inicio=self.generar_fechas(-2), final=self.generar_fechas(8))
        self.orden2 = Orden.objects.create(materia=self.materia1, prestatario=self.prestatario,
                                           lugar=Ubicacion.CAMPUS, estado=EstadoOrden.RESERVADA,
                                           inicio=self.generar_fechas(0), final=self.generar_fechas(8))
        self.orden3 = Orden.objects.create(materia=self.materia1, prestatario=self.prestatario,
                                           lugar=Ubicacion.EXTERNO, estado=EstadoOrden.RESERVADA,
                                           inicio=self.generar_fechas(0), final=self.generar_fechas(4))
        self.orden4 = Orden.objects.create(materia=self.materia1, prestatario=self.prestatario,
                                           lugar=Ubicacion.EXTERNO, estado=EstadoOrden.RESERVADA,
                                           inicio=self.generar_fechas(0), final=self.generar_fechas(9))
        self.orden5 = Orden.objects.create(materia=self.materia1, prestatario=self.prestatario,
                                           lugar=Ubicacion.CAMPUS, estado=EstadoOrden.RESERVADA,
                                           inicio=self.generar_fechas(0), final=self.generar_fechas(4))
        self.orden6 = Orden.objects.create(materia=self.materia1, prestatario=self.prestatario,
                                           lugar=Ubicacion.CAMPUS, estado=EstadoOrden.RESERVADA,
                                           inicio=self.generar_fechas(0), final=make_aware(datetime(2024, 5, 27, 12)))
        
        
        qs1 = self.orden1.asignar_tipo()
        self.assertQuerysetEqual(qs1, TipoOrden.EXTRAORDINARIA)
        
        qs2 = self.orden2.asignar_tipo()
        self.assertQuerysetEqual(qs2, TipoOrden.ORDINARIA)
        
        qs3 = self.orden3.asignar_tipo()
        self.assertQuerysetEqual(qs3, TipoOrden.EXTRAORDINARIA)
        
        qs4 = self.orden4.asignar_tipo()
        self.assertQuerysetEqual(qs4, TipoOrden.EXTRAORDINARIA)
        
        qs5 = self.orden5.asignar_tipo()
        self.assertQuerysetEqual(qs5, TipoOrden.ORDINARIA)
        
        qs6 = self.orden6.asignar_tipo()
        self.assertQuerysetEqual(qs6, TipoOrden.EXTRAORDINARIA)
