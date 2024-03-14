from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User, Group
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth.models import Permission
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.db import models


class Prestatario(User):
    """
    Clase que representa a cualquier persona que pueda sacar
    equipo del almacen
    """

    class Meta:
        proxy = True
        permissions = (
            ("puede_solicitar_equipo", "puede solicitar equipos del almacén"),
            ("puede_ser_corresponsable", "puede ser corresponsable de una orden"),
        )

    class PrestatarioManager(models.Manager):
        def get_queryset(self, *args, **kwargs):
            # filtra los resultados para que únicamente aparezcan
            # los que están en el grupo "prestatarios"
            return super().get_queryset(*args, **kwargs).filter(
                groups__name='prestatarios'
            )

    objects = PrestatarioManager()

    @classmethod
    def crear_grupo(cls):
        """Crea el 'Permission Group' para el usuario prestatario
        los permisos están en la clase Meta"""

        # crear grupo prestatario
        group, created = Group.objects.get_or_create(
            name='prestatarios'
        )

        # permisos del prestatario
        group.permissions.add(Permission.objects.get(
            codename='puede_solicitar_equipo'
        ))

        group.permissions.add(Permission.objects.get(
            codename='puede_ser_corresponsable'
        ))

    def ordenes(self):
        """Órdenes de prestatario"""
        pass

    def reportes(self):
        """Reportes de prestatario"""
        pass

    def suspendido(self) -> bool:
        """Sí el usuario está suspendido"""
        pass

    def carrito(self):
        """Carrito de prestatario"""
        pass

    def materias(self):
        """Materias de prestatario"""
        pass


class Coordinador(User):
    """
    Clase que representa el coordenador
    """

    class CoordinadorManager(models.Manager):
        def get_queryset(self, *args, **kwargs):
            return super().get_queryset(*args, **kwargs).filter(
                groups__name='coordinador'
            )

    objects = CoordinadorManager()

    class Meta:
        proxy = True
        permissions = (
            ("puede_autorizar_extraordinarias", "puede autorizar ordenes extraordinarias"),
            ("puede_eliminar_ordenes", "puede eliminar ordenes de prestatario"),
            ("puede_desactivar_reportes", "puede desactivar reportes de los prestatarios"),
        )

    @classmethod
    def crear_grupo(cls):
        # crear grupo prestatario
        group, created = Group.objects.get_or_create(
            name='coordinador'
        )

        # permisos
        group.permissions.add(Permission.objects.get(
            codename='puede_autorizar_extraordinarias'
        ))

        group.permissions.add(Permission.objects.get(
            codename='puede_eliminar_ordenes'
        ))

        group.permissions.add(Permission.objects.get(
            codename='puede_desactivar_reportes'
        ))

    def autorizar(self, orden):
        pass


class Maestro(User):
    """
    Clase que representa el usuario Maestro
    """

    class MaestroManager(models.Manager):
        def get_queryset(self, *args, **kwargs):
            return super().get_queryset(*args, **kwargs).filter(
                groups__name='maestro'
            )

    objects = MaestroManager()

    class Meta:
        proxy = True
        permissions = (
            ("puede_autorizar_ordinarias", "puede autorizar ordenes ordinarias"),
        )

    @classmethod
    def crear_grupo(cls):
        """Crea el 'Permission Group' para el usuario prestatario
        los permisos están en la clase Meta"""

        # crear grupo prestatario
        group, created = Group.objects.get_or_create(
            name='maestro'
        )

        # permisos
        group.permissions.add(Permission.objects.get(
            codename='puede_autorizar_ordinarias'
        ))

    def autorizar(self, orden):
        """Autoriza órdenes ordinarias"""
        pass

    def materias(self):
        """Materias que supervisa el maestro"""
        pass


class Almacen(User):
    class AlmacenManager(models.Manager):
        def get_queryset(self, *args, **kwargs):
            return super().get_queryset(*args, **kwargs).filter(
                groups__name='almacen'
            )

    objects = AlmacenManager()

    class Meta:
        proxy = True
        permissions = (
            ("puede_recibir_equipo", "puede recibir equipo al almacén"),
            ("puede_entregar_equipo", "puede entregar equipo a los prestatarios"),
            ("puede_hacer_ordenes", "puede hacer ordenes ordinarias para otros usuarios"),
            ("puede_ver_ordenes", "puede ver las ordenes de los prestatarios"),
            ("puede_ver_reportes", "puede ver los reportes de los prestatarios"),
        )

    @classmethod
    def crear_grupo(cls):
        """Crea el 'Permission Group' para el usuario"""

        # crear grupo prestatario
        group, created = Group.objects.get_or_create(
            name='almacen'
        )

        # permisos
        group.permissions.add(Permission.objects.get(
            codename='puede_recibir_equipo'
        ))

        group.permissions.add(Permission.objects.get(
            codename='puede_entregar_equipo'
        ))

        group.permissions.add(Permission.objects.get(
            codename='puede_hacer_ordenes'
        ))

        group.permissions.add(Permission.objects.get(
            codename='puede_ver_ordenes'
        ))

        group.permissions.add(Permission.objects.get(
            codename='puede_ver_reportes'
        ))

    def autorizar(self, orden):
        """Autorizar una orden ordinaria"""
        pass

    def reportar(self, orden):
        """Reportar una orden"""
        pass


class Orden(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "PN", _("PENDIENTE")
        RECHAZADA = "RE", _("RECHAZADA")
        APROBADA = "AP", _("APROBADA")

    class Tipo(models.TextChoices):
        ORDINARIA = "OR", _("ORDINARIA")
        EXTRAORDINARIA = "EX", _("EXTRAORDINARIA")

    prestatario = models.OneToOneField(
        to=Prestatario,
        on_delete=models.CASCADE)

    tipo = models.CharField(
        choices=Tipo.choices,
        default=Tipo.ORDINARIA,
        max_length=2
    )

    fecha_emision = models.DateTimeField(
        default=timezone.now
    )

    fecha_recepcion = models.DateTimeField(
        null=True
    )

    fecha_devolucion = models.DateTimeField(
        null=True
    )

    inicio_prestamo = models.DateTimeField(
        null=True
    )

    final_prestamo = models.DateTimeField(
        null=True
    )

    lugar = models.CharField(
        default="",
        max_length=250
    )

    def unidades(self):
        """Unidades con las que se suplio la orden"""
        pass

    def articulos(self):
        """Articulos en la solicitud"""
        pass

    def estado(self):
        """Estado de la Orden (PENDIENTE, RECHAZADA o APROVADA)"""
        pass

    def reporte(self):
        """Retorna el reporte de la Orden o nada"""
        pass


class Carrito(models.Model):
    prestatario = models.OneToOneField(
        to=User,
        on_delete=models.CASCADE
    )

    inicio_prestamo = models.DateTimeField(
        default=timezone.now,
        null=False
    )

    final_prestamo = models.DateTimeField(
        default=timezone.now,
        null=False
    )

    def agregar(self, articulo):
        """Agrega un articulo al carrito"""
        pass

    def articulos(self):
        """Articulos en la solicitud"""
        pass

    def ordenar(self):
        """Convierte el carrito en una orden (Transaccion)"""
        pass


class Materia(models.Model):
    class Meta:
        unique_together = (
            ('nombre', 'periodo')
        )

    nombre = models.CharField(
        primary_key=True,
        max_length=250,
        null=False,
        blank=False
    )

    periodo = models.CharField(
        max_length=6,
        null=False,
        blank=False
    )

    def alumnos(self):
        """Lista de alumnos en la clase"""
        pass

    def profesores(self):
        """Lista de profesores en la clase"""
        pass

    def articulos(self):
        """Lista de articulos que se pueden solicitar si se lleva
        esta clase"""
        pass


class Reporte(models.Model):
    class Estado(models.TextChoices):
        ACTIVO = "AC", _("ACTIVO")
        INACTIVO = "IN", _("INACTIVO")

    orden = models.OneToOneField(
        to=Orden,
        on_delete=models.CASCADE
    )

    estado = models.CharField(
        max_length=2,
        choices=Estado.choices,
        default=Estado.ACTIVO
    )

    descripcion = models.TextField(
        null=True,
        blank=True,
        max_length=250
    )

    almacen = models.OneToOneField(
        to=Almacen,
        on_delete=models.CASCADE
    )


class Articulo(models.Model):
    class Meta:
        unique_together = (
            ('nombre', 'codigo')
        )

    nombre = models.CharField(
        blank=False,
        null=False,
        max_length=250
    )

    codigo = models.CharField(
        blank=False,
        null=False,
        max_length=250
    )

    def disponible(self, inicio, final):
        """
        Retorna una lista con las unidades disponibles en el rango de
        fechas [inicio, final]
        """
        pass

    def categorias(self):
        """
        Lista de categorias en las que se encuentra el artículo
        """
        pass

    def materias(self):
        """
        Lista de materias en las que se encuentra el artículo
        """
        pass

    def unidades(self):
        """
        Lista de unidades de un artículo
        """
        pass


class Unidad(models.Model):
    class Estado(models.TextChoices):
        ACTIVO = "AC", _("ACTIVO")
        INACTIVO = "IN", _("INACTIVO")

    articulo = models.OneToOneField(
        to=Articulo,
        on_delete=models.CASCADE
    )

    estado = models.CharField(
        max_length=2,
        choices=Estado.choices,
        default=Estado.ACTIVO
    )

    num_control = models.CharField(
        max_length=250,
        unique=True,
        blank=False
    )

    num_serie = models.CharField(
        max_length=250
    )


class Categoria(models.Model):
    nombre = models.CharField(
        primary_key=True,
        max_length=250
    )

    def articulos(self):
        """Articulos que pertenecen a esta categoria"""
        pass


class AutorizacionAlmacen(models.Model):
    class Meta:
        unique_together = (
            ('orden', 'almacen')
        )

    orden = models.OneToOneField(
        to=Orden,
        on_delete=models.CASCADE
    )

    almacen = models.OneToOneField(
        to=Almacen,
        on_delete=models.CASCADE
    )

    autorizar = models.BooleanField(
        default=False
    )


class AutorizacionCoordinador(models.Model):
    class Meta:
        unique_together = (
            ('orden', 'coordinador')
        )

    orden = models.OneToOneField(
        to=Orden,
        on_delete=models.CASCADE
    )

    coordinador = models.OneToOneField(
        to=Coordinador,
        on_delete=models.CASCADE
    )

    autorizar = models.BooleanField(
        default=False
    )


# Relaciones
# -----

class PrestatarioMateria(models.Model):
    class Meta:
        unique_together = (
            ('materia', 'prestatario')
        )

    materia = models.OneToOneField(
        to=Carrito,
        on_delete=models.CASCADE
    )

    prestatario = models.OneToOneField(
        to=Prestatario,
        on_delete=models.CASCADE
    )


class ArticuloMateria(models.Model):
    materia = models.OneToOneField(
        to=Materia,
        on_delete=models.CASCADE
    )

    articulo = models.OneToOneField(
        to=Articulo,
        on_delete=models.CASCADE
    )


class ArticuloCarrito(models.Model):
    class Meta:
        unique_together = (
            ('articulo', 'carrito')
        )

    articulo = models.OneToOneField(
        to=Articulo,
        on_delete=models.CASCADE
    )

    carrito = models.OneToOneField(
        to=Carrito,
        on_delete=models.CASCADE
    )


class CategoriaArticulo(models.Model):
    articulo = models.OneToOneField(
        to=Articulo,
        on_delete=models.CASCADE
    )

    categoria = models.OneToOneField(
        to=Categoria,
        on_delete=models.CASCADE
    )


class UnidadOrden(models.Model):
    unidad = models.OneToOneField(
        to=Unidad,
        on_delete=models.CASCADE
    )

    orden = models.OneToOneField(
        to=Orden,
        on_delete=models.CASCADE
    )
