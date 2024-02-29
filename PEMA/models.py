from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User


class Prestatario(models.Model):
    """
    Relacionado con la clase `User` de Django, representa a un usuario
    que puede solicitar equipo del Almacen.
    """

    user = models.OneToOneField(
        to=User,
        on_delete=models.CASCADE
    )

    num_telefono = models.CharField(
        max_length=10,
        blank=False
    )

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
    """
    Description
    -----------
    Representa una orden de préstamo con detalles como tipo, lugar,
    emisión, recepción y devolución.


    Attributes
    ----------
    emision: models DateTimeField
        Fecha y hora a la que se emitio la orden
    recepcion: models DateTimeField
        Fecha y hora a la que se recogió la orden del almacen
    devolucion: models DateTimeField
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


# Modelos


class Carrito(models.Model):
    """
    Representa el carrito de un prestatario con detalles como la fecha de
    inicio y finalización del préstamo.
    """

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
    """
    Representa una materia académica con un nombre y un período
    asociado.
    """

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


class Coordinador(models.Model):
    """
    Representa a un coordinador.
    """

    user = models.OneToOneField(
        to=User,
        on_delete=models.CASCADE
    )

    def autorizar(self, orden):
        """Autorizar una orden extraordinaria"""
        pass


class Almacen(models.Model):
    """
    Representa un almacen
    """

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
    """
    Reporte del estado del equipo en caso de daños.
    """

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
