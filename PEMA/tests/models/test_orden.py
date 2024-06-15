from datetime import datetime
from django.test import TestCase
from django.utils.timezone import make_aware
from PEMA.models import Prestatario, Articulo, Orden, Reporte, Almacen, Materia, Ubicacion, EstadoOrden, \
    AutorizacionEstado, \
    CorresponsableOrden, TipoOrden


class TestOrden(TestCase):
    @staticmethod
    def generar_fechas(hora):
        return make_aware(datetime(2024, 5, 24, 12 + hora))

    def setUp(self):
        # usuarios
        self.prestatario = Prestatario.crear_usuario(id=0, username="<NAME>", password="<PASSWORD>")
        self.almacen = Almacen.crear_usuario(id=1, username="<NAME2>", password="<PASSWORD>")

        # crear artículos
        self.articulo1 = Articulo.objects.create(nombre="Articulo 1", codigo="100")
        self.articulo2 = Articulo.objects.create(nombre="Articulo 2", codigo="200")

        # crear unidades
        self.unidad1, _ = self.articulo1.crear_unidad(num_control="000", num_serie="000")
        self.unidad2, _ = self.articulo2.crear_unidad(num_control="100", num_serie="200")

        materia = Materia.objects.create(nombre="Fotografia", year=2022, semestre=1)

        self.orden_ordinaria = Orden.objects.create(prestatario=self.prestatario, materia=materia,
                                                    inicio=self.generar_fechas(0),
                                                    final=self.generar_fechas(6),
                                                    tipo=TipoOrden.ORDINARIA)

        self.orden_extraordinaria = Orden.objects.create(prestatario=self.prestatario, materia=materia,
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
        self.orden_ordinaria.agregar_unidad(self.unidad1)
        self.orden_ordinaria.agregar_unidad(self.unidad1)
        self.assertEqual(len(self.orden_ordinaria.articulos()), 1, msg="Hay mas articulos registrados")
        self.orden_ordinaria.agregar_unidad(self.unidad2)
        self.assertEqual(len(self.orden_ordinaria.articulos()), 2, msg="Hay menos articulos registrados")
        self.assertIn(member=self.articulo1, container=self.orden_ordinaria.articulos(),
                      msg="Articulo1 No existe en la orden")
        self.assertIn(member=self.articulo2, container=self.orden_ordinaria.articulos(),
                      msg="Articulo2 No existe en la orden")

    def test_reporte(self):
        almacen = Almacen.get_user(self.almacen)
        self.assertIsNone(self.orden_ordinaria.reporte(), msg="Ya existe un reporte")
        self.orden_ordinaria.reportar(almacen=almacen, descripcion="Nada")
        self.assertIsNotNone(obj=self.orden_ordinaria.reporte(), msg="No existe un reporte")
        self.orden_ordinaria.reportar(almacen=almacen, descripcion="Nada")
        self.assertEqual(len(Reporte.objects.filter(orden=self.orden_ordinaria)), 1)

    def test_entregada(self):
        self.assertFalse(self.orden_ordinaria.entregada())
        self.orden_ordinaria.estado = EstadoOrden.APROBADA
        self.orden_ordinaria.entregar(entregador=self.almacen)
        self.assertTrue(self.orden_ordinaria.entregada())

    def test_rechazar(self):
        self.assertFalse(self.orden_ordinaria.cancelada())
        self.orden_ordinaria.cancelar()
        self.assertTrue(self.orden_ordinaria.cancelada())

    def test_entregar(self):
        self.assertFalse(self.orden_ordinaria.entregada())
        self.orden_ordinaria.estado = EstadoOrden.APROBADA
        self.orden_ordinaria.entregar(entregador=self.almacen)
        self.assertEqual(self.orden_ordinaria.estado, EstadoOrden.ENTREGADA)

    def test_estado_corresponsables(self):
        prest1 = Prestatario.crear_usuario("P1", "password")
        prest2 = Prestatario.crear_usuario("P2", "password")
        self.orden_ordinaria.agregar_corresponsable(prest2)
        self.orden_ordinaria.agregar_corresponsable(prest1)
        autorizaciones_corresponsables = CorresponsableOrden.objects.all()
        self.assertEqual(autorizaciones_corresponsables.count(), 2)
        self.assertEqual(self.orden_ordinaria.estado_corresponsables(), AutorizacionEstado.PENDIENTE)
        cualquiera = autorizaciones_corresponsables.first()
        cualquiera.estado = AutorizacionEstado.RECHAZADA
        cualquiera.save()
        self.assertEqual(self.orden_ordinaria.estado_corresponsables(), AutorizacionEstado.RECHAZADA)
        autorizaciones_corresponsables.update(estado=AutorizacionEstado.ACEPTADA)
        self.assertEqual(self.orden_ordinaria.estado_corresponsables(), AutorizacionEstado.ACEPTADA)

    def test_asignar_tipo(self):
        self.prestatario = Prestatario.crear_usuario(id="123", username="test", password="<PASSWORD>")
        self.materia1 = Materia.objects.create(nombre='Cinematografia', year=2024, semestre=1)
        orden1 = Orden.objects.create(materia=self.materia1, prestatario=self.prestatario, lugar=Ubicacion.CAMPUS,
                                      estado=EstadoOrden.RESERVADA, inicio=self.generar_fechas(-2),
                                      final=self.generar_fechas(8))
        orden2 = Orden.objects.create(materia=self.materia1, prestatario=self.prestatario, lugar=Ubicacion.CAMPUS,
                                      estado=EstadoOrden.RESERVADA, inicio=self.generar_fechas(0),
                                      final=self.generar_fechas(8))
        orden3 = Orden.objects.create(materia=self.materia1, prestatario=self.prestatario, lugar=Ubicacion.EXTERNO,
                                      estado=EstadoOrden.RESERVADA, inicio=self.generar_fechas(0),
                                      final=self.generar_fechas(4))
        orden4 = Orden.objects.create(materia=self.materia1, prestatario=self.prestatario, lugar=Ubicacion.EXTERNO,
                                      estado=EstadoOrden.RESERVADA, inicio=self.generar_fechas(0),
                                      final=self.generar_fechas(9))
        orden5 = Orden.objects.create(materia=self.materia1, prestatario=self.prestatario, lugar=Ubicacion.CAMPUS,
                                      estado=EstadoOrden.RESERVADA, inicio=self.generar_fechas(0),
                                      final=self.generar_fechas(4))
        orden6 = Orden.objects.create(materia=self.materia1, prestatario=self.prestatario, lugar=Ubicacion.CAMPUS,
                                      estado=EstadoOrden.RESERVADA, inicio=self.generar_fechas(0),
                                      final=make_aware(datetime(2024, 5, 27, 12)))

        self.assertEqual(orden1.tipo, TipoOrden.EXTRAORDINARIA)
        self.assertEqual(orden2.tipo, TipoOrden.ORDINARIA)
        self.assertEqual(orden3.tipo, TipoOrden.EXTRAORDINARIA)
        self.assertEqual(orden4.tipo, TipoOrden.EXTRAORDINARIA)
        self.assertEqual(orden5.tipo, TipoOrden.ORDINARIA)
        self.assertEqual(orden6.tipo, TipoOrden.EXTRAORDINARIA)
