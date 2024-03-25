import datetime

from django.contrib.auth.models import User, Group
from django.test import TestCase

from PEMA.models import Almacen, Orden, Prestatario, Entrega, Devolucion, Reporte


class TestCaseAlmacen(TestCase):
    def test_crear_orden(self):
        Prestatario.crear_grupo()
        Almacen.crear_grupo()

        user_almacen = User.objects.create(
            id=0,
            username="almacen_prueba",
            password="<PASSWORD>"
        )

        user_prestatario = User.objects.create(
            id=21,
            username="prestatario_prueba",
            password="<PASSWORD>"
        )

        my_group = Group.objects.get(name='almacen')
        my_group.user_set.add(user_almacen)

        my_group = Group.objects.get(name='prestatarios')
        my_group.user_set.add(user_prestatario)

        orden = Orden.objects.create(
            prestatario=user_prestatario,
            lugar='Un lugar',
            inicio=datetime.datetime.now(datetime.timezone.utc),
            final=datetime.datetime.now(datetime.timezone.utc),
        )

        self.assertEqual(orden.prestatario, user_prestatario)
        self.assertEqual(orden.estado_atr, 'PN')
        self.assertEqual(orden.tipo, 'OR')
        self.assertEqual(orden.lugar, 'Un lugar')

    def test_metodo_entregar(self):
        Prestatario.crear_grupo()
        Almacen.crear_grupo()

        user_almacen = Almacen.objects.create(
            id=0,
            username="almacen_prueba",
            password="<PASSWORD>"
        )

        user_prestatario = User.objects.create_user(
            id=21,
            username="prestatario_prueba",
            password="<PASSWORD>"
        )

        grupo_almacen = Group.objects.get(name='almacen')
        grupo_prestatario = Group.objects.get(name='prestatarios')

        user_almacen.groups.add(grupo_almacen)
        user_prestatario.groups.add(grupo_prestatario)

        orden = Orden.objects.create(
            prestatario=user_prestatario,
            lugar='Un lugar',
            inicio=datetime.datetime.now(datetime.timezone.utc),
            final=datetime.datetime.now(datetime.timezone.utc),
        )

        user_almacen.entregar(orden)
        orden_entrega = Entrega.objects.get(orden=orden)
        self.assertEqual(orden_entrega.orden_id, orden.id)

    def test_metodo_devolver(self):
        Prestatario.crear_grupo()
        Almacen.crear_grupo()

        user_almacen = Almacen.objects.create(
            id=0,
            username="almacen_prueba",
            password="<PASSWORD>"
        )

        user_prestatario = User.objects.create_user(
            id=21,
            username="prestatario_prueba",
            password="<PASSWORD>"
        )

        grupo_almacen = Group.objects.get(name='almacen')
        grupo_prestatario = Group.objects.get(name='prestatarios')

        user_almacen.groups.add(grupo_almacen)
        user_prestatario.groups.add(grupo_prestatario)

        orden = Orden.objects.create(
            prestatario=user_prestatario,
            lugar='Un lugar',
            inicio=datetime.datetime.now(datetime.timezone.utc),
            final=datetime.datetime.now(datetime.timezone.utc),
        )

        user_almacen.devolver(orden)
        orden_devolucion = Devolucion.objects.get(orden=orden)
        self.assertEqual(orden_devolucion.orden_id, orden.id)

    def test_metodo_reportar(self):
        Prestatario.crear_grupo()
        Almacen.crear_grupo()

        user_almacen = Almacen.objects.create(
            id=0,
            username="almacen_prueba",
            password="<PASSWORD>"
        )

        user_prestatario = User.objects.create_user(
            id=21,
            username="prestatario_prueba",
            password="<PASSWORD>"
        )

        grupo_almacen = Group.objects.get(name='almacen')
        grupo_prestatario = Group.objects.get(name='prestatarios')

        user_almacen.groups.add(grupo_almacen)
        user_prestatario.groups.add(grupo_prestatario)

        orden = Orden.objects.create(
            prestatario=user_prestatario,
            lugar='Un lugar',
            inicio=datetime.datetime.now(datetime.timezone.utc),
            final=datetime.datetime.now(datetime.timezone.utc),
        )

        otra_orden = Orden.objects.create(
            prestatario=user_prestatario,
            lugar='Otro lugar',
            inicio=datetime.datetime.now(datetime.timezone.utc),
            final=datetime.datetime.now(datetime.timezone.utc),
        )

        # La orden se le crea reporte
        user_almacen.reportar(orden, 'El equipo llego dañado...')
        orden_reportada = Reporte.objects.get(orden=orden)
        self.assertEqual(orden_reportada.orden_id, orden.id)
        self.assertEqual(orden_reportada.descripcion, 'El equipo llego dañado...')