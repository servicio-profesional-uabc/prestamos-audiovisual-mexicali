from phonenumber_field.modelfields import PhoneNumberField

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.db.models.query import QuerySet


class Prestatario(User):
    """
    Clase que representa un prestatario, que es un usuario con
    permisos específicos para solicitar equipos del almacén y ser
    corresponsable de órdenes.
    """

    class Meta:
        proxy = True
        permissions = (
            ("puede_solicitar_equipo", "Puede solicitar equipos del almacén"),
            ("puede_ser_corresponsable", "Puede ser corresponsable de una orden"),
        )

    class PrestatarioManager(models.Manager):
        def get_queryset(self, *args, **kwargs):
            return super().get_queryset(*args, **kwargs).filter(
                groups__name='prestatarios'
            )

    objects = PrestatarioManager()

    @classmethod
    def crear_grupo(cls):
        """
        Crea el 'Permission Group' para el usuario prestatario.
        """
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

    def ordenes(self) -> 'QuerySet[Orden]':
        """
        Devuelve las órdenes del prestatario.

        Returns:
            QuerySet[Orden]: Lista de órdenes del prestatario.
        """
        pass

    def reportes(self) -> 'QuerySet[Reporte]':
        """
        Devuelve los reportes del prestatario.

        Returns:
            QuerySet[Reporte]: Lista de reportes del prestatario.
        """
        pass

    def materias(self) -> 'QuerySet[Materia]':
        """
        Devuelve las materias del prestatario.

        Returns:
            QuerySet[Materia]: Lista de materias del prestatario.
        """
        pass

    def carrito(self) -> 'Carrito':
        """
        Devuelve el carrito del prestatario.

        Returns:
            Carrito: El carrito del prestatario.
        """
        pass

    def suspendido(self) -> bool:
        """
        Verifica si el usuario está suspendido.

        Returns:
            bool: Verdadero si el usuario está suspendido, Falso de lo contrario.
        """
        # un usuario está suspendido si tiene algún reporte activo
        pass


class Coordinador(User):
    """
    Clase que representa al coordinador, con permisos específicos
    para autorizar órdenes, eliminar órdenes de prestatarios y
    desactivar reportes de prestatarios.
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
        """
        Método de clase para crear el grupo de coordinadores y
        asignarles permisos.
        """

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

    def autorizar(self, orden: 'Orden') -> None:
        """
        Autoriza una orden específica.

        Args:
            orden (Orden): La orden que se va a autorizar.

        Returns:
            None
        """
        pass


class Maestro(User):
    """
    Clase que representa el usuario Maestro.
    """

    class MaestroManager(models.Manager):
        """
        Manejador de objetos para los maestros.
        """

        def get_queryset(self, *args, **kwargs):
            """
            Obtiene el queryset filtrado por grupos de maestros.

            Args:
                *args: Argumentos adicionales posicionales.
                **kwargs: Argumentos adicionales de palabras clave.

            Returns:
                queryset: Queryset filtrado de maestros.
            """
            return super().get_queryset(*args, **kwargs).filter(
                groups__name='maestro'
            )

    objects = MaestroManager()

    class Meta:
        proxy = True
        permissions = (
            ("puede_autorizar_ordinarias", "Puede autorizar órdenes ordinarias"),
        )

    @classmethod
    def crear_grupo(cls):
        """
        Crea el 'Permission Group' para el usuario maestro.
        """
        # crear grupo maestro
        group, created = Group.objects.get_or_create(
            name='maestro'
        )

        # permisos
        group.permissions.add(Permission.objects.get(
            codename='puede_autorizar_ordinarias'
        ))

    def autorizar(self, orden: 'Orden'):
        """
        Autoriza órdenes ordinarias.

        Args:
            orden (Orden): La orden que se va a autorizar.

        Returns:
            None
        """
        pass

    def materias(self) -> 'QuerySet[Materia]':
        """
        Materias que supervisa el maestro.

        Returns:
            QuerySet[Materia]: Materias supervisadas por el maestro.
        """
        pass


class Almacen(User):
    """
    Clase que representa al usuario Almacén.
    """

    class AlmacenManager(models.Manager):
        def get_queryset(self, *args, **kwargs):
            """
            Obtiene el queryset filtrado por grupos de almacén.

            Args:
                *args: Argumentos adicionales posicionales.
                **kwargs: Argumentos adicionales de palabras clave.

            Returns:
                queryset: Queryset filtrado del almacén.
            """
            return super().get_queryset(*args, **kwargs).filter(
                groups__name='almacen'
            )

    objects = AlmacenManager()

    class Meta:
        """
        Metadatos de la clase Almacén.
        """
        proxy = True
        permissions = (
            ("puede_recibir_equipo", "Puede recibir equipo al almacén"),
            ("puede_entregar_equipo", "Puede entregar equipo a los prestatarios"),
            ("puede_hacer_ordenes", "Puede hacer órdenes ordinarias para otros usuarios"),
            ("puede_ver_ordenes", "Puede ver las órdenes de los prestatarios"),
            ("puede_ver_reportes", "Puede ver los reportes de los prestatarios"),
        )

    @classmethod
    def crear_grupo(cls):
        """
        Crea el 'Permission Group' para el usuario almacén.
        """
        # crear grupo almacén
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

    def autorizar(self, orden: 'Orden') -> None:
        """
        Autoriza una orden ordinaria.

        Args:
            orden (Orden): La orden que se va a autorizar.

        Returns:
            None
        """
        pass

    def reportar(self, orden: 'Orden') -> None:
        """
        Reporta una orden.

        Args:
            orden (Orden): La orden que se va a reportar.

        Returns:
            None
        """
        pass


class Perfil(models.Model):
    """
    Información adicional del usuario.
    """

    usuario = models.OneToOneField(
        to=User,
        on_delete=models.CASCADE
    )

    imagen = models.ImageField(
        default='default.png'
    )

    phone = PhoneNumberField(
        null=True
    )

    @staticmethod
    def info(cls, user: User) -> 'Perfil':
        """
        Obtiene el perfil asociado a un usuario dado.

        Args:
            cls
            user (User): El usuario del cual se desea obtener el perfil.

        Returns:
            Perfil: El perfil asociado al usuario.
        """
        pass


class Orden(models.Model):
    """
    Clase que representa una orden del almacén.
    """

    class Estado(models.TextChoices):
        """
        Opciones para el estado de la orden.
        """
        PENDIENTE = "PN", _("PENDIENTE")
        RECHAZADA = "RE", _("RECHAZADA")
        APROBADA = "AP", _("APROBADA")

    class Tipo(models.TextChoices):
        """
        Opciones para el tipo de orden.
        """
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

    lugar = models.CharField(
        default="",
        null="",
        max_length=250
    )

    inicio = models.DateTimeField(
        null=False
    )

    final = models.DateTimeField(
        null=False
    )

    def unidades(self) -> 'QuerySet[Unidad]':
        """
        Devuelve las unidades con las que se suplió la orden.

        Returns:
            QuerySet[Unidad]: Unidades asociadas a la orden.
        """
        pass

    def articulos(self) -> 'QuerySet[Articulo]':
        """
        Devuelve los artículos en la orden.

        Returns:
            QuerySet[Articulo]: Artículos asociados a la orden.
        """
        pass

    def reporte(self) -> 'Reporte':
        """
        Retorna el reporte de la Orden o nada si no tiene reporte.

        Returns:
            Reporte: Reporte asociado a la orden o None si no tiene reporte.
        """
        pass

    def estado(self) -> str:
        """
        Devuelve el estado de la Orden.

        Returns:
            str: Estado de la orden (PENDIENTE, RECHAZADA o APROBADA).
        """
        pass


class Materia(models.Model):
    """
    Clase que representa una materia.
    """

    class Meta:
        """
        Metadatos de la clase Materia.
        """
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

    def alumnos(self) -> QuerySet[User]:
        """
        Devuelve la lista de alumnos en la clase.

        Returns:
            QuerySet[User]: Lista de usuarios (alumnos) asociados a la materia.
        """
        pass

    def profesores(self) -> QuerySet[User]:
        """
        Devuelve la lista de profesores en la clase.

        Returns:
            QuerySet[User]: Lista de usuarios (profesores) asociados a la materia.
        """
        pass

    def articulos(self) -> 'QuerySet[Articulo]':
        """
        Devuelve la lista de artículos que se pueden solicitar si se lleva esta clase.

        Returns:
            QuerySet[Articulo]: Lista de artículos asociados a la materia.
        """
        pass


class Carrito(models.Model):
    """
    Clase que representa un carrito de compras.
    """

    prestatario = models.OneToOneField(
        to=User,
        on_delete=models.CASCADE
    )

    materia = models.OneToOneField(
        to=Materia,
        on_delete=models.DO_NOTHING
    )

    inicio = models.DateTimeField(
        default=timezone.now,
        null=False
    )

    final = models.DateTimeField(
        default=timezone.now,
        null=False
    )

    def agregar(self, articulo) -> None:
        """
        Agrega un artículo al carrito.

        Args:
            articulo: El artículo que se va a agregar al carrito.

        Returns:
            None
        """
        pass

    def articulos(self) -> 'QuerySet[Articulo]':
        """
        Devuelve los artículos en el carrito.

        Returns:
            QuerySet[Articulo]: Artículos en el carrito.
        """
        pass

    def ordenar(self) -> None:
        """
        Convierte el carrito en una orden (Transacción).

        Returns:
            None
        """
        pass


class Reporte(models.Model):
    """
    Clase que representa un reporte.
    """

    class Meta:
        unique_together = (
            ('almacen', 'orden')
        )

    class Estado(models.TextChoices):
        """
        Opciones para el estado del reporte.
        """
        ACTIVO = "AC", _("ACTIVO")
        INACTIVO = "IN", _("INACTIVO")

    almacen = models.OneToOneField(
        to=Almacen,
        on_delete=models.CASCADE
    )

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

    fecha = models.DateTimeField(
        auto_now_add=True
    )


class Articulo(models.Model):
    """
    Clase que representa un artículo.
    """

    class Meta:
        """
        Metadatos de la clase Artículo.
        """
        unique_together = (
            ('nombre', 'codigo')
        )

    imagen = models.ImageField(
        default='default.png'
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

    descripcion = models.TextField(
        null=True,
        blank=True,
        max_length=250
    )

    def disponible(self, inicio, final) -> 'QuerySet[Unidad]':
        """
        Retorna una lista con las unidades disponibles en el rango de
        fecha y hora [inicio, final].

        Args:
            inicio: Fecha y hora de inicio del rango.
            final: Fecha y hora de finalización del rango.

        Returns:
            QuerySet[Unidad]: Unidades disponibles en el rango especificado.
        """
        pass

    def categorias(self) -> 'QuerySet[Categoria]':
        """
        Devuelve la lista de categorías en las que se encuentra el artículo.

        Returns:
            QuerySet[Categoria]: Categorías asociadas al artículo.
        """
        pass

    def materias(self) -> QuerySet[Materia]:
        """
        Devuelve la lista de materias en las que se encuentra el artículo.

        Returns:
            QuerySet[Materia]: Materias asociadas al artículo.
        """
        pass

    def unidades(self) -> 'QuerySet[Unidad]':
        """
        Devuelve la lista de unidades de un artículo.

        Returns:
            QuerySet[Unidad]: Unidades asociadas al artículo.
        """
        pass


class Entrega(models.Model):
    """
    Clase que representa una entrega.
    """

    orden = models.OneToOneField(
        to=Orden,
        on_delete=models.CASCADE,
        primary_key=True
    )

    almacen = models.OneToOneField(
        to=Almacen,
        on_delete=models.CASCADE
    )

    fecha = models.DateTimeField(
        auto_now_add=True
    )


class Devolucion(models.Model):
    """
    Clase que representa una devolución.
    """

    orden = models.OneToOneField(
        to=Orden,
        on_delete=models.CASCADE,
        primary_key=True
    )

    almacen = models.OneToOneField(
        to=Almacen,
        on_delete=models.CASCADE
    )

    fecha = models.DateTimeField(
        auto_now_add=True
    )


class Unidad(models.Model):
    """
    Clase que representa una unidad de un artículo.
    """

    class Estado(models.TextChoices):
        """
        Opciones para el estado de la unidad.
        """
        ACTIVO = "AC", _("ACTIVO")
        INACTIVO = "IN", _("INACTIVO")

    articulo = models.OneToOneField(
        to=Articulo,
        on_delete=models.CASCADE
    )

    estado = models.CharField(
        max_length=2,
        choices=Estado.choices,
        null=False,
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
    """
    Clase que representa una categoría.
    """

    nombre = models.CharField(
        primary_key=True,
        max_length=250
    )

    def articulos(self):
        """
        Devuelve los artículos que pertenecen a esta categoría.
        """
        pass


class AutorizacionOrdinaria(models.Model):
    """
    Clase que representa una autorización ordinaria.
    """

    class Meta:
        unique_together = (
            ('orden', 'maestro')
        )

    orden = models.OneToOneField(
        to=Orden,
        on_delete=models.CASCADE
    )

    maestro = models.OneToOneField(
        to=Almacen,
        on_delete=models.CASCADE
    )

    autorizar = models.BooleanField(
        default=False
    )


class AutorizacionExtraordinaria(models.Model):
    """
    Clase que representa una autorización extraordinaria.
    """

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


class CorresponsableOrden(models.Model):
    """
    Clase que representa un corresponsable de una orden.
    """

    class Meta:
        unique_together = (
            ('orden', 'prestatario')
        )

    prestatario = models.OneToOneField(
        to=Prestatario,
        on_delete=models.CASCADE,
    )

    orden = models.OneToOneField(
        to=Orden,
        on_delete=models.CASCADE
    )

    aceptado = models.BooleanField(
        default=False,
    )


class PrestatarioMateria(models.Model):
    """
    Clase que representa la relación entre un prestatario y una materia.
    """

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
    """
    Clase que representa la relación entre un artículo y una materia.
    """

    materia = models.OneToOneField(
        to=Materia,
        on_delete=models.CASCADE
    )

    articulo = models.OneToOneField(
        to=Articulo,
        on_delete=models.CASCADE
    )


class ArticuloCarrito(models.Model):
    """
    Clase que representa la relación entre un artículo y un carrito.
    """

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
    """
    Clase que representa la relación entre una categoría y un artículo.
    """

    articulo = models.OneToOneField(
        to=Articulo,
        on_delete=models.CASCADE
    )

    categoria = models.OneToOneField(
        to=Categoria,
        on_delete=models.CASCADE
    )


class UnidadOrden(models.Model):
    """
    Clase que representa la relación entre una unidad y una orden.
    """

    unidad = models.OneToOneField(
        to=Unidad,
        on_delete=models.CASCADE
    )

    orden = models.OneToOneField(
        to=Orden,
        on_delete=models.CASCADE
    )
