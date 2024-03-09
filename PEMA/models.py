from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User, Group
from django.contrib.auth.models import Permission

from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import User
from django.db import models


class PrestatarioManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        """Limita los resultados de prestatarios unicamente a los
        usuarios en ese grupo"""

        return super().get_queryset(*args, **kwargs).filter(
            groups__name='prestatarios'
        )


class Prestatario(User):
    class Meta:
        proxy = True
        permissions = (
            ("puede_solicitar_equipo", "puede solicitar equipos del almacén"),
            ("puede_ser_corresponsable", "puede ser corresponsable de una orden"),
        )

    objects = PrestatarioManager()

    @staticmethod
    def crear_grupo():
        """Crea el 'Permission Group' para el usuario prestatario
        los permisos están en 'Prestatario.Meta.permissions'"""

        try:
            group, created = Group.objects.get_or_create(
                name='prestatarios'
            )

            # permisos definidos en 'Prestatario.Meta.permissions'
            permisos_prestatario = Permission.objects.filter(
                content_type__model='prestatario'
            )

            # si el grupo ya existe no se vuleve a crear
            if not created:
                print("Info: El grupo 'prestatarios' ya existe.")

            # agregar los permisos al usuarios
            for permiso in permisos_prestatario:
                print(permiso)
                group.permissions.add(permiso)

        except Exception as e:
            print(f"Error in Prestatario.crear_grupo: {e}")

    def save(self, *args, **kwargs):
        """Crea un usuario y lo agrega al grupo prestatario"""

        try:
            group = Group.objects.get(name="prestatarios")

            super().save(*args, **kwargs)
            self.groups.add(group)
        except Group.DoesNotExist:
            print("Error in Prestatario.save: El grupo 'prestatarios' no existe.")

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


class Orden(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "PN", _("PENDIENTE")
        RECHAZADA = "RE", _("RECHAZADA")
        APROVADA = "AP", _("APROVADA")

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
        to=Prestatario,
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
        """Lista de articulos que se pueden solicitar si se lleva esta clase"""
        pass


class Almacen(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    def autorizar(self, orden):
        """Autorizar una orden ordinaria"""
        pass

    def reportar(self, orden):
        """Reportar una orden"""
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
        Lista de unidades de un articulo
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


class Coordinador(models.Model):
    user = models.OneToOneField(
        to=User,
        on_delete=models.CASCADE
    )

    def autorizar(self, Orden):
        """Autorizar una orden extraordinaria"""
        pass


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
