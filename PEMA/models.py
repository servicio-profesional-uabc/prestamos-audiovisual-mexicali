from datetime import datetime
from typing import Any

from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.db.models.query import QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


# Roles de Usuario

class Prestatario(User):
    """
    Es un tipo de usuario con permisos específicos para solicitar
    equipos del almacén y ser corresponsable de órdenes.
    """

    class Meta:
        verbose_name_plural = "Prestatarios"
        proxy = True

    class PrestatarioManager(models.Manager):
        def get_queryset(self, *args, **kwargs):
            return super().get_queryset(*args, **kwargs).filter(groups__name='prestatarios')

    objects = PrestatarioManager()

    @staticmethod
    def get_user(user: User) -> Any | None:
        """
        Obtiene el usuario prestatario

        :param user: Usuario del que se quiere obtener el prestatario
        :returns: Prestatario o None si no es Prestatario
        """

        try:
            return Prestatario.objects.get(pk=user.pk)
        except Prestatario.DoesNotExist:
            return None

    @staticmethod
    def crear_usuario(*args, **kwargs) -> 'Prestatario':
        """
        Crea un usuario de tipo prestatario, util para hacer pruebas unitarias

        :returns: usuario en el grupo de Prestatarios
        """

        grupo, _ = Prestatario.crear_grupo()
        user = User.objects.create_user(*args, **kwargs)
        grupo.user_set.add(user)

        return Prestatario.get_user(user)

    @staticmethod
    def crear_grupo() -> tuple[Any, bool]:
        """
        Crea el 'Permission Group' para el usuario prestatario.

        :returns: grupo y sí se creo
        """

        # crear grupo prestatario
        group, created = Group.objects.get_or_create(name='prestatarios')

        # permisos del prestatario
        group.permissions.add(Permission.objects.get(codename='add_carrito'))
        group.permissions.add(Permission.objects.get(codename='add_orden'))
        group.permissions.add(Permission.objects.get(codename='add_corresponsableorden'))

        return group, created

    def ordenes(self) -> QuerySet[Any]:
        """
        Órdenes que ha realizado el usuario.

        :return: Lista de órdenes del usuario.
        """
        return Orden.objects.filter(_corresponsables__in=[self])

    def reportes(self) -> QuerySet['Reporte']:
        """
        Devuelve los reportes del prestatario.

        :returns: Lista de reportes del prestatario.
        """

        return Reporte.objects.filter(orden__in=self.ordenes())

    def materias(self) -> QuerySet['Materia']:
        """
        Devuelve las materias del prestatario.
        """

        return self.materia_set.all()

    def carrito(self) -> Any | None:
        """
        Devuelve el carrito actual del prestatario, el usuario solo
        puede tener un carrito a la vez

        :return:  El carrito del prestatario o None si no existe.
        """

        try:
            return Carrito.objects.get(prestatario=self)
        except Carrito.DoesNotExist:
            return None

    def suspendido(self) -> bool:
        """
        Verifica si el usuario está suspendido.

        :returns: Si el usuario está suspendido del sistema
        """

        return self.reportes().filter(estado=Reporte.Estado.ACTIVO).exists()


class Coordinador(User):
    """
    Clase que representa al coordinador, con permisos específicos
    para autorizar órdenes, eliminar órdenes de prestatarios y
    desactivar reportes de prestatarios.
    """

    class CoordinadorManager(models.Manager):
        def get_queryset(self, *args, **kwargs):
            return super().get_queryset(*args, **kwargs).filter(groups__name='coordinador')

    objects = CoordinadorManager()

    class Meta:
        verbose_name_plural = "Coordinadores"
        proxy = True

    @staticmethod
    def solicitar_autorizacion(orden: 'Orden'):
        # TODO: que hacer si no hay coordinador
        # TODO: enviar los correos
        for coordinador in Coordinador.objects.all():
            AutorizacionOrden.objects.create(autorizador=coordinador, orden=orden, tipo=orden.tipo)

    @classmethod
    def crear_grupo(cls) -> tuple[Any, bool]:
        """
        Crea el grupo de permisos para Coordinadores.

        :returns: Grupo de Coordinadores y si se creó el grupo.
        """

        # grupo
        group, created = Group.objects.get_or_create(name='coordinador')

        # permisos
        group.permissions.add(Permission.objects.get(codename='add_autorizacionorden'))
        group.permissions.add(Permission.objects.get(codename='delete_orden'))
        group.permissions.add(Permission.objects.get(codename='change_reporte'))

        return group, created

    @classmethod
    def crear_usuario(cls, *args, **kwargs) -> User:
        """
        :returns: usuario en el grupo
        """
        grupo, _ = cls.crear_grupo()
        user = User.objects.create_user(*args, **kwargs)
        grupo.user_set.add(user)

        return user


class Maestro(User):
    """
    Un maestro puede autorizar órdenes ordinarias y ser el
    supervisor de una clase.
    """

    class MaestroManager(models.Manager):
        def get_queryset(self, *args, **kwargs):
            return super().get_queryset(*args, **kwargs).filter(groups__name='maestro')

    objects = MaestroManager()

    class Meta:
        verbose_name_plural = "Maestros"
        proxy = True

    @staticmethod
    def get_user(user: User) -> Any | None:
        try:
            return Maestro.objects.get(pk=user.pk)
        except Maestro.DoesNotExist:
            return None

    @staticmethod
    def solicitar_autorizacion(orden: 'Orden'):
        # TODO: que hacer si no hay maestro asignado a la clase
        # TODO: evnviar los correos
        for maestro in orden.materia.maestros():
            AutorizacionOrden.objects.create(autorizador=maestro, orden=orden, tipo=orden.tipo)

    @staticmethod
    def crear_grupo() -> tuple[Any, bool]:
        """
        Crea el 'Permission Group' para el usuario maestro.

        :returns: El grupo y sí se creó
        """

        # grupo
        group, created = Group.objects.get_or_create(name='maestro')

        # permisos
        group.permissions.add(Permission.objects.get(codename='add_autorizacionorden'))
        group.permissions.add(Permission.objects.get(codename='change_autorizacionorden'))

        return group, created

    @classmethod
    def crear_usuario(cls, *args, **kwargs) -> User:
        """Crea un usuario de tipo prestatario"""

        grupo, _ = cls.crear_grupo()
        user = User.objects.create_user(*args, **kwargs)
        grupo.user_set.add(user)

        return user

    def __str__(self):
        return f"{self.first_name}"


class Almacen(User):
    """
    Clase que representa al usuario Almacén, Un usuario almacen 
    puede surtir las Órdenes de los prestatarios también se encarga
    de recibir el equipo.
    """

    class AlmacenManager(models.Manager):
        def get_queryset(self, *args, **kwargs):
            return super().get_queryset(*args, **kwargs).filter(groups__name='almacen')

    objects = AlmacenManager()

    class Meta:
        verbose_name_plural = "Encargados de Almacén"
        proxy = True

    @staticmethod
    def get_user(user: User) -> Any | None:
        """
        Obtiene el usuario Almacen.

        :param user: Usuario del que se quiere obtener el Almacen.
        :returns: Prestatario o None si no es Almacen.
        """
        try:
            return Almacen.objects.get(pk=user.pk)
        except Almacen.DoesNotExist:
            return None

    @staticmethod
    def crear_grupo() -> tuple['Group', bool]:
        """
        Crea el 'Permission Group' para el usuario almacén.

        :returns: El grupo creado y sí se creó el grupo
        """
        # crear grupo almacén
        group, created = Group.objects.get_or_create(name='almacen')

        # permisos
        group.permissions.add(Permission.objects.get(codename='view_articulo'))
        group.permissions.add(Permission.objects.get(codename='add_devolucion'))
        group.permissions.add(Permission.objects.get(codename='view_devolucion'))
        group.permissions.add(Permission.objects.get(codename='add_entrega'))
        group.permissions.add(Permission.objects.get(codename='view_entrega'))
        group.permissions.add(Permission.objects.get(codename='add_orden'))
        group.permissions.add(Permission.objects.get(codename='delete_orden'))
        group.permissions.add(Permission.objects.get(codename='view_orden'))
        group.permissions.add(Permission.objects.get(codename='add_reporte'))
        group.permissions.add(Permission.objects.get(codename='change_reporte'))
        group.permissions.add(Permission.objects.get(codename='delete_reporte'))
        group.permissions.add(Permission.objects.get(codename='view_reporte'))
        group.permissions.add(Permission.objects.get(codename='view_unidad'))

        return group, created

    @staticmethod
    def crear_usuario(*args, **kwargs) -> User:
        """
        Crea un usuario de tipo prestatario
        """

        grupo, _ = Almacen.crear_grupo()
        user = User.objects.create_user(*args, **kwargs)
        grupo.user_set.add(user)

        return user


# Modelos

class Perfil(models.Model):
    """
    Esta clase proporciona acceso a todos los datos de un usuario.
    Se implementa para evitar complicar el modelo de usuario de
    Django. Además, este método facilita el acceso a los datos que ya
    están incluidos mediante métodos específicos.

    :ivar usuario: Usuario del perfil.
    :ivar telefono: Número de teléfono.
    """

    usuario = models.OneToOneField(to=User, on_delete=models.CASCADE)
    telefono = PhoneNumberField(null=True)

    @classmethod
    def user_data(cls, user: User) -> tuple['Perfil', bool]:
        """
        :param user: El usuario del cual se desea obtener el perfil.
        :returns: El perfil asociado al usuario.
        """

        return Perfil.objects.get_or_create(usuario=user)

    def email(self) -> str:
        """
        :return: Obtener el email del perfil
        """
        return self.usuario.email

    def apellido(self) -> str:
        """
        :return: Obtener el apellido del usuario.
        """
        return self.usuario.last_name

    def nombre(self) -> str:
        """
        Nombre real de usuario.

        :return: Obtener el nombre del usuario.
        """
        return self.usuario.first_name

    def username(self) -> str:
        """
        Nombre del usuario en el sistema, en el proyecto el nombre
        del usuario siempre corresponde a la matrícula o al número
        de empleado.

        :return: Nombre de usuario.
        """
        return self.usuario.username


class Materia(models.Model):
    """
    Las materias se encargan de limitar el material al que pueden acceder
    los Prestatarios.

    :ivar nombre: Nombre de la clase
    :ivar year: Año que se imparte la clase.
    :ivar semestre: Semestre que se imparte la clase.
    :ivar activa: Si la clase se está impartiendo actualmente.
    """

    class Meta:
        unique_together = ('nombre', 'year', 'semestre')

    nombre = models.CharField(primary_key=True, max_length=250, null=False, blank=False)
    year = models.IntegerField(null=False)
    semestre = models.IntegerField(null=False)
    activa = models.BooleanField(default=True)

    _articulos = models.ManyToManyField(to='Articulo', blank=True)
    _alumnos = models.ManyToManyField(to=User, blank=True)
    _maestros = models.ManyToManyField(to=Maestro, blank=True, related_name='materias_profesor')

    def alumnos(self) -> QuerySet['User']:
        """
        :returns: Lista de alumnos de la materia.
        """
        return self._alumnos.all()

    def maestros(self) -> QuerySet['Maestro']:
        """
        :returns: Lista de profesores asociados a la materia.
        """
        return self._maestros.all()

    def articulos(self):
        """
        :returns: Lista de artículos disponibles para la materia.
        """
        return self._articulos.all()

    def agregar_articulo(self, articulo: 'Articulo'):
        """
        :param articulo: Artículo que se quiere agregar.
        :returns: ArticuloMateria agregado y sí se creó el objeto.
        """
        return self._articulos.add(articulo)

    def agregar_maestro(self, maestro: 'Maestro'):
        """
        :param maestro:
        :return:
        """
        return self._maestros.add(maestro)

    def agregar_alumno(self, usuario: 'User'):
        """
        :param usuario: Participante que se agregara como alumno a la Materia.
        :return:
        """
        return self._alumnos.add(usuario)

    def __str__(self):
        return f"{self.nombre} ({self.year}-{self.semestre})"


class TipoOrden(models.TextChoices):
    """Opciones para el tipo de orden."""
    ORDINARIA = "OR", _("Ordinaria")
    EXTRAORDINARIA = "EX", _("Extraordinaria")


class EstadoOrden(models.TextChoices):
    """
     * `PENDIENTE_CR`: Esperando confirmación de los corresponsables.
     * `PENDIENTE_AP`: Esperando aprobación del maestro o coordinador
     * `RECHAZADA`: Orden rechazada por el maestro o coordinador.
     * `APROBADA`: Orden aprobada por el maestro o coordinador.
     * `CANCELADA`: Orden cancelado por el prestatario.
    """
    PENDIENTE_CR = "PC", _("Esperando corresponsables")
    PENDIENTE_AP = "PA", _("Esperando autorización")
    RECHAZADA = "RE", _("Rechazada")
    APROBADA = "AP", _("Aprobada")
    CANCELADA = "CN", _("Cancelada")


class Articulo(models.Model):
    """
    Clase que representa un artículo.

    :param nombre: Nombre.
    :param codigo: Identificador.
    :param descripcion: Descripción breve.
    :param imagen: Imagen.
    """

    class Meta:
        unique_together = ('nombre', 'codigo')

    imagen = models.ImageField(default='default.png')
    nombre = models.CharField(blank=False, null=False, max_length=250)
    codigo = models.CharField(blank=True, null=False, max_length=250)
    descripcion = models.TextField(null=True, blank=True, max_length=250)
    _categorias = models.ManyToManyField(to='Categoria', blank=True)

    def crear_unidad(self, num_control: str, num_serie: str) -> tuple['Unidad', bool]:
        """
        Registrar una unidad de un Artículo.

        :param num_control: Número de control de la unidad.
        :param num_serie: Número de seríe de la unidad.
        """

        return Unidad.objects.get_or_create(articulo=self, num_control=num_control, num_serie=num_serie)

    def disponible(self, inicio, final) -> 'QuerySet[Unidad]':
        """
        Lista con las unidades disponibles en el rango [inicio, final].

        :param inicio: Fecha y hora de inicio del rango.
        :param final: Fecha y hora de finalización del rango.

        :returns: Unidades disponibles en el rango especificado.
        """

        ordenesAprobadas = Orden.objects.filter(estado="AP")
        # ordenesConflicto = []
        unidadesConflicto = []
        idConflicto = []
        for ord in ordenesAprobadas:
            if (ord.inicio == inicio or ord.final == final or (ord.inicio < inicio and ord.final > inicio) or (
                    ord.inicio < final and ord.final > final) or (ord.inicio > inicio and ord.final < final)):
                # ordenesConflicto.append(ord)
                unidadesConflicto.append(ord.unidades())
        for unid in unidadesConflicto:
            for unidad in unid:
                idConflicto.append(unidad.num_control)

        return Unidad.objects.difference(Unidad.objects.filter(num_control__in=idConflicto))

    def categorias(self) -> QuerySet['Categoria']:
        """Devuelve la lista de categorías en las que pertenece el artículo."""
        return self._categorias.all()

    def materias(self) -> QuerySet['Materia']:
        """
        Lista de materias en las que se encuentra el artículo.

        :returns: Materias asociadas al artículo.
        """

        return self.materia_set.all()

    def unidades(self) -> 'QuerySet[Unidad]':
        """
        Devuelve la lista de unidades de un artículo.

        :returns: Unidades asociadas al artículo.
        """

        return Unidad.objects.filter(articulo=self)

    def __str__(self):
        return f"{self.codigo}-{self.nombre}"


class Unidad(models.Model):
    """
    Clase que representa una unidad de un artículo.

    :ivar articulo: Al que pertenece la unidad
    :ivar estado: De la unidad
    :ivar num_control: Para identificar la unidad
    :ivar num_serie: De la unidad
    """

    class Meta:
        verbose_name_plural = "Unidades"
        unique_together = ('articulo', 'num_control')

    class Estado(models.TextChoices):
        ACTIVO = "AC", _("ACTIVO")
        INACTIVO = "IN", _("INACTIVO")

    articulo = models.ForeignKey(to=Articulo, on_delete=models.CASCADE)
    estado = models.CharField(max_length=2, choices=Estado.choices, null=False, default=Estado.ACTIVO)
    num_control = models.CharField(max_length=250, null=False, blank=False)
    num_serie = models.CharField(blank=False, null=False, max_length=250)

    def ordenes(self) -> QuerySet['Orden']:
        return Orden.objects.filter(unidadorden__unidad=self)

    def __str__(self):
        return f"{self.num_control}-{self.num_control}-{self.articulo.nombre}"


class Orden(models.Model):
    """
    Una orden es un conjunto de Unidades de cada Artículo definido
    el Carrito, para que el encargado del Almacén sepa
    específicamente que entregar.

    .. warning::
        Utilizar ``estado`` unicamente en filtros

    :ivar materia: Materia de la orden.
    :ivar inicio: Fecha de inicio de la orden.
    :ivar final: Fecha de devolución de la orden.

    :ivar nombre: Nombre de la produccion.
    :ivar descripcion: Información adicional de la orden.

    :ivar tipo: Tipo de orden, ordinaria o extraordinaria.
    :ivar lugar: Lugar donde se usara el material.
    :ivar estado: Guarda el último estado de la orden.
    :ivar emision: Fecha de emisión de la orden.
    """

    class Meta:
        ordering = ("emision",)
        verbose_name_plural = "Ordenes"

    class Tipo(models.TextChoices):
        """Opciones para el tipo de orden."""
        ORDINARIA = "OR", _("Ordinaria")
        EXTRAORDINARIA = "EX", _("Extraordinaria")

    class Ubicacion(models.TextChoices):
        """Opciones para el lugar de la orden"""
        CAMPUS = "CA", _("Campus")
        EXTERNO = "EX", _("Externo")

    # obligatorio
    nombre = models.CharField(blank=False, null=False, max_length=250)
    prestatario = models.ForeignKey(to=User, on_delete=models.CASCADE)
    materia = models.ForeignKey(to=Materia, on_delete=models.DO_NOTHING)
    tipo = models.CharField(default=TipoOrden.ORDINARIA, choices=TipoOrden.choices, max_length=2)
    lugar = models.CharField(default=Ubicacion.CAMPUS, choices=Ubicacion.choices, max_length=2)
    descripcion_lugar = models.CharField(blank=False, null=True, max_length=125)
    estado = models.CharField(default=EstadoOrden.PENDIENTE_CR, choices=EstadoOrden.choices, max_length=2)

    inicio = models.DateTimeField(null=False)
    final = models.DateTimeField(null=False)

    descripcion = models.TextField(blank=True, max_length=512)

    # opcional
    _corresponsables = models.ManyToManyField(to=Prestatario, related_name='corresponsables')
    _unidades = models.ManyToManyField(to=Unidad, blank=True)

    # automático
    emision = models.DateTimeField(auto_now_add=True)

    def agregar_prestatario(self, prestatario: 'Prestatario'):
        self._corresponsables.add(prestatario)

    def es_ordinaria(self) -> bool:
        return self.tipo == TipoOrden.ORDINARIA

    def es_extraordinaria(self):
        return self.tipo == TipoOrden.EXTRAORDINARIA

    def unidades(self) -> 'QuerySet[Unidad]':
        """
        Devuelve las unidades con las que se suplió la orden.
        """
        return self._unidades.all()

    def articulos(self) -> 'QuerySet[Articulo]':
        """
        Devuelve los artículos en la orden.
        """
        return Articulo.objects.filter(unidad__in=self.unidades())

    def reporte(self) -> 'Reporte':
        """
        Retorna el Reporte de la Orden o nada sí no tiene reporte.
        """
        return Reporte.objects.filter(orden=self).first()

    def agregar_unidad(self, unidad: 'Unidad'):
        """
        Agrega una unidad a la orden.
        """
        return self._unidades.add(unidad)

    def estado_corresponsables(self) -> str:
        corresponsables_orden = CorresponsableOrden.objects.filter(orden=self)
        estados = set([orden.estado for orden in corresponsables_orden])

        if CorresponsableOrden.Estado.RECHAZADA in estados:
            # Sí alguno de los corresponsables rechazo la orden
            return CorresponsableOrden.Estado.RECHAZADA

        if CorresponsableOrden.Estado.PENDIENTE in estados:
            # Si todavía faltán corresponsables de aceptar
            return CorresponsableOrden.Estado.PENDIENTE

        if len(estados) == 1 and CorresponsableOrden.Estado.ACEPTADA in estados:
            # Si todos los corresponsables aceptaron
            return CorresponsableOrden.Estado.ACEPTADA

        # TODO: ¿Qué hacer sí ocurre un error?, En mi opinión se debería enviar un correo al administrador

    def entregar(self, almacen: 'Almacen') -> tuple['Entrega', bool]:
        """
        Generar el registro que el Almacén entrego el equipo.

        :param almacen: Almacén que entrega el equipo.
        :returns: Registro de entrega y si el registro se creó
        """

        return Entrega.objects.get_or_create(almacen=almacen, orden=self)

    def recibir(self, almacen: 'Almacen') -> tuple['Devolucion', bool]:
        """
        Generar el registro que el Almacén recibió el equipo de vuelta.

        :param almacen: Almacén que recibe el equipo.
        :returns: El registro de devolución, si el registro se creó
        """

        return Devolucion.objects.get_or_create(almacen=almacen, orden=self)

    def reportar(self, almacen: 'Almacen', descripcion: str) -> tuple['Reporte', bool]:
        """
        Este método genera un Reporte para una orden solicitada. Las órdenes
        reportadas utilizando este método siempre se consideran activas.
        Si se desea desactivar el informe, se requiere la intervención de un
        Coordinador.

        :param almacen: Almacén que reporta la orden.
        :param descripcion: Información adicional del Reporte.
        :returns: Reporte y sí el objeto se creó.
        """

        return Reporte.objects.get_or_create(almacen=almacen, orden=self, descripcion=descripcion)

    def __str__(self):
        return f"{self.prestatario}"


class Carrito(models.Model):
    """
    La clase que representa un carrito de compras se utiliza para
    seleccionar los artículos del catálogo. Una vez que los artículos
    han sido seleccionados, el carrito puede convertirse en una Orden.

    :ivar prestatario: Usuario dueño del carrito
    :ivar materia: Materia a la que está ligado el equipo del carrito.
    :ivar inicio: Fecha de inicio del préstamo.
    :ivar final: Fecha de devolución del préstamo.
    """

    prestatario = models.OneToOneField(to=Prestatario, on_delete=models.CASCADE)
    materia = models.ForeignKey(to=Materia, on_delete=models.DO_NOTHING)
    inicio = models.DateTimeField(default=timezone.now, null=False)
    final = models.DateTimeField(default=timezone.now, null=False)
    _articulos = models.ManyToManyField(to='ArticuloCarrito', blank=True)

    def agregar(self, articulo: 'Articulo', unidades: int):
        """
        Agrega un artículo al carrito.

        :param articulo: El artículo que se va a agregar.
        :param unidades: Unidades que se va a agregar del Artículo.
        """
        if not self._articulos.filter(articulo=articulo).exists():
            # si no esta registrado este articulo
            foo = ArticuloCarrito.objects.create(propietario=self, articulo=articulo, unidades=unidades)
            self._articulos.add(foo)
            return

        data = self._articulos.get(articulo=articulo)
        data.unidades = unidades
        data.save()

    def articulos(self) -> QuerySet['Articulo']:
        """
        Devuelve los artículos en el carrito.
        :returns: Artículos en el carrito.
        """

        return self._articulos.all()

    def ordenar(self) -> None:
        """
        Convierte el carrito en una orden (Transacción).

        :returns: None
        """

        # TODO: Verificar si la orden es Ordinaria o Extraordinaria

        with transaction.atomic():
            orden = Orden.objects.create(
                prestatario=self.prestatario,
                nombre=f"{self.prestatario.username}{self.inicio}",
                materia=self.materia,
                inicio=self.inicio,
                final=self.final
            )

            orden.agregar_prestatario(self.prestatario)

            # TODO: convertir los ArticuloCarrito a UnidadOrden

            CorresponsableOrden.objects.create(prestatario=self.prestatario, orden=orden)

            self.delete()

            # TODO: enviar correo a los Cooresponsables


class Reporte(models.Model):
    """
    Clase que representa un reporte a una Orden.

    :param almacen: Usuario que emitió el reporte.
    :param orden: Orden a la que se refiere el reporte.
    :param estado: Estado de la orden.automatico
    :param descripcion: Información de la orden.
    :param emision: Fecha de emisión del reporte.
    """

    class Meta:
        unique_together = ('almacen', 'orden')

    class Estado(models.TextChoices):
        """Opciones para el estado del reporte."""
        ACTIVO = "AC", _("ACTIVO")
        INACTIVO = "IN", _("INACTIVO")

    almacen = models.ForeignKey(to=Almacen, on_delete=models.CASCADE)
    orden = models.ForeignKey(to=Orden, on_delete=models.CASCADE)
    estado = models.CharField(max_length=2, choices=Estado.choices, default=Estado.ACTIVO)
    descripcion = models.TextField(null=True, blank=True, max_length=250)
    emision = models.DateTimeField(auto_now_add=True)


class Categoria(models.Model):
    """
    Clase que representa una categoría.

    :ivar nombre (str): Nombre de la categoría
    """

    nombre = models.CharField(primary_key=True, max_length=250)

    def articulos(self) -> QuerySet['Articulo']:
        """
        Devuelve los artículos que pertenecen a esta categoría.

        :return: Artículos que pertenecen a la Categoría
        """

        return self.articulo_set.all()

    def agregar(self, articulo: 'Articulo'):
        """
        Agrega un Articulo a la Categoría
        """
        self.articulo_set.add(articulo)

    def __str__(self):
        return f"{self.nombre}"


class Entrega(models.Model):
    """
    Entrega al almacen. Se genera cada vez que Almacen entrega el
    equipo al Prestatario.

    :param almacen: Encargado del Almacen.
    :param orden: Orden que se entrega.
    :param emision: Fecha en la que se hace la emisión.
    """

    orden = models.OneToOneField(to=Orden, on_delete=models.CASCADE, primary_key=True)
    almacen = models.ForeignKey(to=Almacen, on_delete=models.CASCADE)
    emision = models.DateTimeField(auto_now_add=True)


class Devolucion(models.Model):
    """
    Devolución del equipo al Almacén se genera cada vez que
    Prestatario devuelve el equipo al Almacén.

    :ivar orden: Orden que se devuelve
    :ivar almacen: Responsable del almacén
    :ivar emision: Fecha de emisión
    """

    orden = models.OneToOneField(to=Orden, on_delete=models.CASCADE, primary_key=True)
    almacen = models.OneToOneField(to=Almacen, on_delete=models.CASCADE)
    emision = models.DateTimeField(auto_now_add=True)


# Autorizaciones

class Autorizacion(models.Model):
    class Meta:
        abstract = True

    class Estado(models.TextChoices):
        """
        Opciones para el estado de la orden:
            * PENDIENTE: Esperando confirmación.
            * RECHAZADA: Corresponsabilidad rechazada.
            * ACEPTADA: Corresponsabilidad aceptada.
        """
        PENDIENTE = "PN", _("Pendiente")
        RECHAZADA = "RE", _("Rechazada")
        ACEPTADA = "AC", _("Aceptada")

    estado = models.CharField(default=Estado.PENDIENTE, choices=Estado.choices, max_length=2)

    def esta_pendiente(self) -> bool:
        return self.estado == self.Estado.PENDIENTE

    def aceptada(self) -> bool:
        return self.estado == self.Estado.ACEPTADA

    def rechazada(self) -> bool:
        return self.estado == self.Estado.RECHAZADA

    def aceptar(self):
        self.estado = self.Estado.ACEPTADA

    def rechazar(self):
        self.estado = self.Estado.RECHAZADA


class AutorizacionOrden(Autorizacion):
    class Meta:
        verbose_name_plural = "Autorizaciones"
        unique_together = ('orden', 'autorizador')

    autorizador = models.ForeignKey(to=User, on_delete=models.CASCADE)
    orden = models.ForeignKey(to=Orden, on_delete=models.CASCADE)
    tipo = models.CharField(default=TipoOrden.ORDINARIA, choices=TipoOrden.choices, max_length=2)

    def __str__(self):
        return f"({self.get_tipo_display()}) {self.orden}"


class CorresponsableOrden(Autorizacion):
    """
    Corresponsable de una orden.

    :ivar prestatario: Usuario que acepta ser corresponsable.
    :ivar orden: Orden de la que el prestatario es corresponsable.
    """

    class Meta:
        unique_together = ('orden', 'prestatario')

    prestatario = models.ForeignKey(to=Prestatario, on_delete=models.CASCADE)
    orden = models.ForeignKey(to=Orden, on_delete=models.CASCADE)


# Clases de relación

class ArticuloCarrito(models.Model):
    """
    Relación entre un Artículo y un Carrito.

    :ivar articulo: Artículo que se encuentra en el carrito.
    :ivar unidades: Número de unidades que se van a solicitar del artículo.
    """
    propietario = models.ForeignKey(to=Carrito, on_delete=models.CASCADE, null=True)
    articulo = models.ForeignKey(to=Articulo, on_delete=models.CASCADE)
    unidades = models.IntegerField(default=0)

    def __str__(self):
        return f"({self.unidades}) {self.articulo}"
