from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User


class Prestatario(models.Model):
    user = models.OneToOneField(
        to=User,
        on_delete=models.CASCADE
    )


class Carrito(models.Model):
    prestatario = models.OneToOneField(
        to=Prestatario,
        on_delete=models.CASCADE
    )

    inicio = models.DateTimeField(
        default=timezone.now,
        null=False
    )

    final = models.DateTimeField(
        default=timezone.now,
        null=False
    )


class Profesor(models.Model):
    prestatario = models.OneToOneField(
        to=Prestatario,
        on_delete=models.CASCADE
    )

    num_emplado = models.CharField(
        max_length=250,
        primary_key=True
    )


class Alumno(models.Model):
    class Meta:
        unique_together = (
            ('prestatario', 'matricula')
        )

    prestatario = models.OneToOneField(
        to=Prestatario,
        on_delete=models.CASCADE
    )

    matricula = models.CharField(
        max_length=250,
        primary_key=True
    )


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

class AlumnoMateria(models.Model):
    class Meta:
        unique_together = (
            ('alumno', 'materia')
        )

    alumno = models.OneToOneField(
        to=Alumno,
        on_delete=models.CASCADE
    )

    materia = models.OneToOneField(
        to=Materia,
        on_delete=models.CASCADE
    )


class Coordinador(models.Model):
    user = models.OneToOneField(
        to=User,
        on_delete=models.CASCADE
    )

class Almacen(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

class Orden(models.Model):
    """
    Attributes
    ----------
    emision : models.DateTimeField
        Fecha y hora a la que se emitio la orden
    recepcion : models.DateTimeField
        Fecha y hora a la que se recogio la orden del almacen
    devolucion: models.DateTimeField
        Fecha y hora a la que se devolvio la orden al almacen
    """

    class Estado(models.TextChoices):
        PENDIENTE = "PN", _("PENDIENTE")
        RECHAZADA = "RE", _("RECHAZADA")
        APROVADA = "AP", _("APROVADA")

    class Tipo(models.TextChoices):
        ORDINARIA = "OR", _("ORDINARIA")
        EXTRAORDINARIA = "EX", _("EXTRAORDINARIA")

    prestatario = models.OneToOneField(
        to=Prestatario,
        on_delete=models.CASCADE
    )

    tipo = models.CharField(
        choices=Tipo.choices,
        default=Tipo.ORDINARIA,
        max_length=2
    )

    lugar = models.CharField(
        default="",
        max_length=250
    )

    emision = models.DateTimeField(
        default=timezone.now
    )

    recepcion = models.DateTimeField(
        null=True
    )

    devolucion = models.DateTimeField(
        null=True
    )


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


class Articulo(models.Model):
    codigo = models.CharField(
        primary_key=True,
        max_length=250
    )

    nombre = models.CharField(
        blank=False,
        null=False,
        max_length=250
    )


class Unidad(models.Model):
    class Estado(models.TextChoices):
        ACTIVO = "AC", _("ACTIVO")
        INACTIVO = "IN", _("INACTIVO")

    articulo = models.OneToOneField(
        to=Articulo,
        on_delete=models.CASCADE
    )

    codigo = models.CharField(
        primary_key=True,
        max_length=250
    )

    estado = models.CharField(
        max_length=2,
        choices=Estado.choices,
        default=Estado.ACTIVO
    )


class Categoria(models.Model):
    nombre = models.CharField(
        primary_key=True,
        max_length=250
    )


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


class ProfesorMateria(models.Model):
    class Meta:
        unique_together = (
            ('profesor', 'materia')
        )

    profesor = models.OneToOneField(
        to=Profesor,
        on_delete=models.CASCADE
    )

    materia = models.OneToOneField(
        to=Materia,
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


class ArticuloMateria(models.Model):
    materia = models.OneToOneField(
        to=Materia,
        on_delete=models.CASCADE
    )

    articulo = models.OneToOneField(
        to=Articulo,
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
