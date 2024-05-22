from typing import Any

from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.db.models import Q
from django.db.models.query import QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


# Roles de Usuario

class Prestatario(User):
    """
    Un tipo de usuario con permisos específicos para solicitar
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
        Obtiene el usuario prestatario.

        :param user: El usuario que se quiere obtener.
        :returns: El usuario prestatario o None si no existe.
        """
        try:
            user = Prestatario.objects.get(pk=user.pk)
        except Prestatario.DoesNotExist:
            user = None
        return user

    @staticmethod
    def crear_usuario(*args, **kwargs) -> 'Prestatario':
        """
        Crea un usuario de tipo prestatario. Útil para pruebas unitarias.

        :returns: El usuario prestatario creado.
        """
        grupo, _ = Prestatario.crear_grupo()
        user = User.objects.create_user(*args, **kwargs)
        grupo.user_set.add(user)
        return Prestatario.get_user(user)

    @staticmethod
    def crear_grupo() -> tuple[Any, bool]:
        """
        Crea el grupo de permisos para el usuario prestatario.

        :returns: El grupo creado y si se creó el grupo.
        """
        group, created = Group.objects.get_or_create(name='prestatarios')
        group.permissions.add(Permission.objects.get(codename='add_carrito'))
        group.permissions.add(Permission.objects.get(codename='add_orden'))
        group.permissions.add(Permission.objects.get(codename='add_corresponsableorden'))
        return group, created

    def ordenes(self) -> QuerySet[Any]:
        """
        Obtiene las órdenes realizadas por el usuario.

        :returns: Lista de órdenes del usuario.
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

        :returns: Lista de materias del prestatario.
        """
        return self.materia_set.all()

    def carrito(self) -> QuerySet['Carrito']:
        """
        Devuelve el carrito actual del prestatario. Un usuario solo
        puede tener un carrito a la vez.

        :returns: El carrito del prestatario o None si no existe.
        """
        return Carrito.objects.get(prestatario=self)

    def tiene_carrito(self) -> bool:
        """
        Verifica si el usuario tiene un carrito.

        :returns: True si el usuario tiene un carrito, False en caso contrario.
        """
        return Carrito.objects.filter(prestatario=self).exists()

    def suspendido(self) -> bool:
        """
        Verifica si el usuario está suspendido.

        :returns: True si el usuario está suspendido, False en caso contrario.
        """
        return self.reportes().filter(estado=Reporte.Estado.ACTIVO).exists()


class Coordinador(User):
    """
    Un tipo de usuario con permisos específicos para autorizar órdenes,
    eliminar órdenes de prestatarios y desactivar reportes de prestatarios.
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
        """
        Solicita autorización para una orden.

        :param orden: La orden para la cual se solicita autorización.
        """
        for coordinador in Coordinador.objects.all():
            AutorizacionOrden.objects.create(autorizador=coordinador, orden=orden, tipo=orden.tipo)

    @classmethod
    def crear_grupo(cls) -> tuple[Any, bool]:
        """
        Crea el grupo de permisos para Coordinadores.

        :returns: El grupo de Coordinadores y si se creó el grupo.
        """
        group, created = Group.objects.get_or_create(name='coordinador')
        group.permissions.add(Permission.objects.get(codename='add_autorizacionorden'))
        group.permissions.add(Permission.objects.get(codename='delete_orden'))
        group.permissions.add(Permission.objects.get(codename='change_reporte'))
        return group, created

    @classmethod
    def crear_usuario(cls, *args, **kwargs) -> User:
        """
        Crea un usuario de tipo Coordinador.

        :returns: El usuario creado en el grupo Coordinador.
        """
        grupo, _ = cls.crear_grupo()
        user = User.objects.create_user(*args, **kwargs)
        grupo.user_set.add(user)
        return user


class Maestro(User):
    """
    Un maestro con permisos para autorizar órdenes ordinarias y ser
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
        """
        Obtiene el usuario maestro.

        :param user: El usuario que se quiere obtener.
        :returns: El usuario maestro o None si no existe.
        """
        try:
            return Maestro.objects.get(pk=user.pk)
        except Maestro.DoesNotExist:
            return None

    @staticmethod
    def solicitar_autorizacion(orden: 'Orden'):
        """
        Solicita autorización para una orden.

        :param orden: La orden para la cual se solicita autorización.
        """
        for maestro in orden.materia.maestros():
            AutorizacionOrden.objects.create(autorizador=maestro, orden=orden, tipo=orden.tipo)

    @staticmethod
    def crear_grupo() -> tuple[Any, bool]:
        """
        Crea el grupo de permisos para el usuario maestro.

        :returns: El grupo creado y si se creó el grupo.
        """
        group, created = Group.objects.get_or_create(name='maestro')
        group.permissions.add(Permission.objects.get(codename='add_autorizacionorden'))
        group.permissions.add(Permission.objects.get(codename='change_autorizacionorden'))
        return group, created

    @classmethod
    def crear_usuario(cls, *args, **kwargs) -> User:
        """
        Crea un usuario de tipo Maestro.

        :returns: El usuario creado en el grupo Maestro.
        """
        grupo, _ = Maestro.crear_grupo()
        user = User.objects.create_user(*args, **kwargs)
        grupo.user_set.add(user)
        return user

    def __str__(self):
        return f"{self.first_name}"


class Almacen(User):
    """
    Un usuario de tipo Almacén con permisos para surtir órdenes de
    prestatarios y recibir equipo.
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
        Obtiene el usuario Almacén.

        :param user: El usuario que se quiere obtener.
        :returns: El usuario Almacén o None si no existe.
        """
        try:
            almacen = Almacen.objects.get(pk=user.pk)
        except Almacen.DoesNotExist:
            almacen = None
        return almacen

    @staticmethod
    def crear_grupo() -> tuple['Group', bool]:
        """
        Crea el grupo de permisos para el usuario Almacén.

        :returns: El grupo creado y si se creó el grupo.
        """
        group, created = Group.objects.get_or_create(name='almacen')
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
        Crea un usuario de tipo Almacén.

        :returns: El usuario creado en el grupo Almacén.
        """
        grupo, _ = Almacen.crear_grupo()
        user = User.objects.create_user(*args, **kwargs)
        grupo.user_set.add(user)
        return user


# Modelos

class Perfil(models.Model):
    """
    Proporciona acceso a todos los datos de un usuario, implementado
    para evitar complicar el modelo de usuario de Django.

    :ivar usuario: Usuario del perfil.
    :ivar numero_telefono: Número de teléfono.
    """

    class Meta:
        verbose_name_plural = "Perfiles"

    usuario = models.OneToOneField(to=User, on_delete=models.CASCADE)
    numero_telefono = PhoneNumberField(blank=True, null=False, region='MX')

    @classmethod
    def user_data(cls, user: User) -> 'Perfil':
        """
        Obtiene el perfil asociado a un usuario.

        :param user: El usuario del cual se desea obtener el perfil.
        :returns: El perfil asociado al usuario.
        """
        return Perfil.objects.get(usuario=user)

    def incompleto(self) -> bool:
        """
        Verifica si el perfil está incompleto.

        :returns: True si el perfil está incompleto, False en caso contrario.
        """
        return self.email().strip() == "" or self.telefono().strip() == ""

    def telefono(self) -> str:
        """
        Obtiene el número de teléfono del perfil.

        :returns: El número de teléfono del perfil.
        """
        perfil = Perfil.user_data(user=self.usuario)
        return str(perfil.numero_telefono)

    def email(self) -> str:
        """
        Obtiene el correo electrónico del perfil.

        :returns: El correo electrónico del perfil.
        """
        return str(self.usuario.email)

    def apellido(self) -> str:
        """
        Obtiene el apellido del usuario.

        :returns: El apellido del usuario.
        """
        return self.usuario.last_name

    def nombre(self) -> str:
        """
        Obtiene el nombre del usuario.

        :returns: El nombre del usuario.
        """
        return self.usuario.first_name

    def username(self) -> str:
        """
        Obtiene el nombre de usuario en el sistema.

        :returns: El nombre de usuario.
        """
        return self.usuario.username

    def __str__(self):
        return str(self.usuario)


class Materia(models.Model):
    """
    Representa una materia, que limita el material al que pueden acceder
    los prestatarios.

    :ivar nombre: Nombre de la clase.
    :ivar year: Año en que se imparte la clase.
    :ivar semestre: Semestre en que se imparte la clase.
    :ivar activa: Indica si la clase se está impartiendo actualmente.
    """

    class Meta:
        unique_together = ('nombre', 'year', 'semestre')

    nombre = models.CharField(primary_key=True, max_length=250, null=False, blank=False)
    year = models.IntegerField(null=False)
    semestre = models.IntegerField(null=False)
    activa = models.BooleanField(default=True)

    _articulos = models.ManyToManyField(to='Articulo', blank=True)
    _alumnos = models.ManyToManyField(to=User, blank=True)
    _maestros = models.ManyToManyField(to=User, blank=False, related_name='materias_profesor')

    def alumnos(self) -> QuerySet['User']:
        """
        Obtiene la lista de alumnos de la materia.

        :returns: Lista de alumnos de la materia.
        """
        return self._alumnos.all()

    def maestros(self) -> QuerySet['Maestro']:
        """
        Obtiene la lista de profesores asociados a la materia.

        :returns: Lista de profesores asociados a la materia.
        """
        return self._maestros.all()

    def articulos(self) -> QuerySet['Articulo']:
        """
        Obtiene la lista de artículos disponibles para la materia.

        :returns: Lista de artículos disponibles para la materia.
        """
        return self._articulos.all()

    def agregar_articulo(self, articulo: 'Articulo'):
        """
        Agrega un artículo a la materia.

        :param articulo: El artículo que se quiere agregar.
        """
        self._articulos.add(articulo)

    def agregar_maestro(self, maestro: 'Maestro'):
        """
        Agrega un maestro a la materia.

        :param maestro: El maestro que se quiere agregar.
        """
        self._maestros.add(maestro)

    def agregar_alumno(self, usuario: 'User'):
        """
        Agrega un alumno a la materia.

        :param usuario: El usuario que se quiere agregar como alumno.
        """
        self._alumnos.add(usuario)

    def __str__(self):
        return f"{self.nombre} ({self.year}-{self.semestre})"


class Articulo(models.Model):
    """
    Representa un artículo.

    :param nombre: Nombre del artículo.
    :param codigo: Identificador del artículo.
    :param descripcion: Descripción breve del artículo.
    :param imagen: Imagen del artículo.
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
        Registra una unidad de un artículo.

        :param num_control: Número de control de la unidad.
        :param num_serie: Número de serie de la unidad.
        :returns: La unidad creada y si se creó la unidad.
        """
        return Unidad.objects.get_or_create(articulo=self, num_control=num_control, num_serie=num_serie)

    def disponible(self, inicio, final) -> QuerySet['Unidad']:
        """
        Obtiene la lista de unidades disponibles en un rango de fechas.

        :param inicio: Fecha y hora de inicio del rango.
        :param final: Fecha y hora de finalización del rango.
        :returns: Unidades disponibles en el rango especificado.
        """
        ordenes_reservadas = Orden.objects.filter(
            estado__in=[EstadoOrden.RESERVADA, EstadoOrden.APROBADA, EstadoOrden.ENTREGADA],
            _unidades__in=self.unidades()
        )

        colisiones = ordenes_reservadas.filter(
            Q(inicio=inicio) |
            Q(final=final) |
            Q(inicio__lt=inicio, final__gt=inicio) |
            Q(inicio__lt=final, final__gt=final) |
            Q(inicio__gt=inicio, final__lt=final)
        )

        unidades_reservadas = Unidad.objects.filter(orden__in=colisiones)
        return self.unidades().exclude(id__in=unidades_reservadas)

    def categorias(self) -> QuerySet['Categoria']:
        """
        Obtiene la lista de categorías en las que pertenece el artículo.

        :returns: Lista de categorías en las que pertenece el artículo.
        """
        return self._categorias.all()

    def materias(self) -> QuerySet['Materia']:
        """
        Obtiene la lista de materias en las que se encuentra el artículo.

        :returns: Lista de materias en las que se encuentra el artículo.
        """
        return self.materia_set.all()

    def unidades(self) -> QuerySet['Unidad']:
        """
        Obtiene la lista de unidades de un artículo.

        :returns: Lista de unidades de un artículo.
        """
        return Unidad.objects.filter(articulo=self)

    def __str__(self):
        return self.nombre


class Unidad(models.Model):
    """
    Representa una unidad de un artículo.

    :ivar articulo: Artículo al que pertenece la unidad.
    :ivar estado: Estado de la unidad.
    :ivar num_control: Número de control de la unidad.
    :ivar num_serie: Número de serie de la unidad.
    """

    class Meta:
        verbose_name_plural = "Unidades"
        unique_together = ('articulo', 'num_control', 'num_serie')

    class Estado(models.TextChoices):
        ACTIVO = "AC", _("ACTIVO")
        INACTIVO = "IN", _("INACTIVO")

    articulo = models.ForeignKey(to=Articulo, on_delete=models.CASCADE)
    estado = models.CharField(max_length=2, choices=Estado.choices, null=False, default=Estado.ACTIVO)
    num_control = models.CharField(max_length=250, null=False, blank=False)
    num_serie = models.CharField(blank=False, null=False, max_length=250)

    def ordenes(self) -> QuerySet['Orden']:
        """
        Obtiene la lista de órdenes que incluyen esta unidad.

        :returns: Lista de órdenes que incluyen esta unidad.
        """
        return Orden.objects.filter(unidadorden__unidad=self)

    def __str__(self):
        return f"{self.articulo}"


class TipoOrden(models.TextChoices):
    """
    Opciones para el tipo de orden.
    """
    ORDINARIA = "OR", _("Ordinaria")
    EXTRAORDINARIA = "EX", _("Extraordinaria")


class EstadoOrden(models.TextChoices):
    """
    Define los posibles estados de una orden en el sistema.
    """
    RESERVADA = "RS", _("Pendiente")
    ENTREGADA = "EN", _("Entregada")
    CANCELADA = "CN", _("Cancelada")
    APROBADA = "AP", _("Listo para iniciar")
    DEVUELTA = "DE", _("Devuelta")


class Ubicacion(models.TextChoices):
    """
    Opciones para el lugar de la orden.
    """
    CAMPUS = "CA", _("En el Campus")
    EXTERNO = "EX", _("Fuera del Campus")


class Orden(models.Model):
    """
    Representa una orden de unidades de artículos definidos en el Carrito.

    :ivar nombre: Nombre de la producción.
    :ivar prestatario: Usuario que hace la solicitud.
    :ivar materia: Materia de la orden.
    :ivar tipo: Tipo de orden (ordinaria o extraordinaria).
    :ivar lugar: Lugar donde se usará el material.
    :ivar descripcion_lugar: Descripción específica del lugar.
    :ivar estado: Último estado de la orden.
    :ivar inicio: Fecha de inicio de la orden.
    :ivar final: Fecha de devolución de la orden.
    :ivar descripcion: Información adicional de la orden.
    :ivar emision: Fecha de emisión de la orden.
    """

    class Meta:
        ordering = ("emision",)
        verbose_name_plural = "Órdenes"

    nombre = models.CharField(blank=False, null=False, max_length=250, verbose_name='Nombre Producción')
    prestatario = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name='Emisor')
    materia = models.ForeignKey(to=Materia, on_delete=models.DO_NOTHING)
    tipo = models.CharField(default=TipoOrden.ORDINARIA, choices=TipoOrden.choices, max_length=2, verbose_name="Tipo de la Solicitud")
    lugar = models.CharField(default=Ubicacion.CAMPUS, choices=Ubicacion.choices, max_length=2, verbose_name='Lugar de la Producción')
    descripcion_lugar = models.CharField(blank=False, null=True, max_length=125, verbose_name='Lugar Específico')
    estado = models.CharField(default=EstadoOrden.RESERVADA, choices=EstadoOrden.choices, max_length=2)
    inicio = models.DateTimeField(null=False)
    final = models.DateTimeField(null=False)
    descripcion = models.TextField(blank=False, max_length=512, verbose_name='Descripción de la Producción')
    _corresponsables = models.ManyToManyField(to=User, related_name='corresponsables', verbose_name='Participantes')
    _unidades = models.ManyToManyField(to=Unidad, blank=True, verbose_name='Equipo Solicitado')
    emision = models.DateTimeField(auto_now_add=True)

    def cancelar(self):
        """
        Cancela la orden cambiando su estado a CANCELADA.
        """
        self.estado = EstadoOrden.CANCELADA

    def cancelada(self) -> bool:
        """
        Verifica si la orden está cancelada.

        :returns: True si la orden está cancelada, False en caso contrario.
        """
        return self.estado == EstadoOrden.CANCELADA

    def aprobar(self):
        """
        Aprueba la orden cambiando su estado a APROBADA.
        """
        self.estado = EstadoOrden.APROBADA

    def entregada(self) -> bool:
        """
        Verifica si la orden ha sido entregada.

        :returns: True si la orden ha sido entregada, False en caso contrario.
        """
        return self.estado == EstadoOrden.ENTREGADA and Entrega.objects.filter(orden=self).exists()

    def entregar(self, entregador: 'User'):
        """
        Marca la orden como entregada.

        :param entregador: El usuario que entrega la orden.
        """
        if self.estado in [EstadoOrden.CANCELADA, EstadoOrden.DEVUELTA]:
            return

        entrega, _ = Entrega.objects.get_or_create(entregador=entregador, orden=self)
        self.estado = EstadoOrden.ENTREGADA
        self.save()

    def corresponsables(self) -> QuerySet['Prestatario']:
        """
        Obtiene la lista de corresponsables de la orden.

        :returns: Lista de corresponsables de la orden.
        """
        return self._corresponsables.all()

    def agregar_corresponsable(self, prestatario: 'Prestatario'):
        """
        Agrega un corresponsable a la orden.

        :param prestatario: El prestatario que se quiere agregar como corresponsable.
        """
        self._corresponsables.add(prestatario)

    def asignar_tipo(self):
        self.tipo == TipoOrden.ORDINARIA
        delta = self.final - self.inicio
        if(self.lugar == Ubicacion.EXTERNO or (delta.total_seconds() / (60*60)) > 8):
            self.tipo = TipoOrden.EXTRAORDINARIA
        return self.tipo
    
    def es_ordinaria(self) -> bool:
        """
        Verifica si una orden es ordinaria.

        :returns: True si la orden es ordinaria, False en caso contrario.
        """
        return self.tipo == TipoOrden.ORDINARIA

    def es_extraordinaria(self) -> bool:
        """
        Verifica si una orden es extraordinaria.

        :returns: True si la orden es extraordinaria, False en caso contrario.
        """
        return self.tipo == TipoOrden.EXTRAORDINARIA

    def unidades(self) -> QuerySet['Unidad']:
        """
        Obtiene la lista de unidades que se suplió la orden.

        :returns: Lista de unidades que se suplió la orden.
        """
        return self._unidades.all()

    def articulos(self) -> QuerySet['Articulo']:
        """
        Obtiene la lista de artículos en la orden.

        :returns: Lista de artículos en la orden.
        """
        return Articulo.objects.filter(unidad__in=self.unidades())

    def reporte(self) -> Any | None:
        """
        Obtiene el reporte de la orden, si existe.

        :returns: El reporte de la orden o None si no existe.
        """
        return Reporte.objects.filter(orden=self).first()

    def agregar_unidad(self, unidad: 'Unidad'):
        """
        Agrega una unidad a la orden.

        :param unidad: La unidad que se quiere agregar.
        """
        self._unidades.add(unidad)

    def solicitar_autorizacion(self):
        """
        Solicita autorización para la orden acorde al tipo.
        """
        
        if self.es_ordinaria():
            Maestro.solicitar_autorizacion(self)
        elif self.es_extraordinaria():
            Coordinador.solicitar_autorizacion(self)

    def estado_corresponsables(self) -> str:
        """
        Obtiene el estado de los corresponsables de la orden.

        :returns: Estado de los corresponsables de la orden.
        """
        corresponsables_orden = CorresponsableOrden.objects.filter(orden=self)
        estados = set([orden.estado for orden in corresponsables_orden])

        if AutorizacionEstado.RECHAZADA in estados:
            return AutorizacionEstado.RECHAZADA
        if AutorizacionEstado.PENDIENTE in estados:
            return AutorizacionEstado.PENDIENTE
        if len(estados) == 1 and AutorizacionEstado.ACEPTADA in estados:
            return AutorizacionEstado.ACEPTADA

    def recibir(self, almacen: 'Almacen') -> tuple['Devolucion', bool]:
        """
        Genera el registro de devolución indicando que el Almacén recibió el equipo de vuelta.

        :param almacen: El usuario Almacén que recibe el equipo.
        :returns: El registro de devolución y si se creó el registro.
        """
        return Devolucion.objects.get_or_create(emisor=almacen, orden=self)

    def reportar(self, almacen: 'Almacen', descripcion: str) -> tuple['Reporte', bool]:
        """
        Genera un reporte para la orden. Los reportes generados siempre se consideran activos.

        :param almacen: El usuario Almacén que reporta la orden.
        :param descripcion: Descripción adicional del reporte.
        :returns: El reporte creado y si se creó el reporte.
        """
        return Reporte.objects.get_or_create(emisor=almacen, orden=self, descripcion=descripcion)

    def __str__(self):
        return f"{self.prestatario}"


class Carrito(models.Model):
    """
    Representa un carrito de compras utilizado para seleccionar artículos
    del catálogo. El carrito puede convertirse en una Orden.

    :ivar prestatario: Usuario dueño del carrito.
    :ivar materia: Materia a la que está ligado el equipo del carrito.
    :ivar inicio: Fecha de inicio del préstamo.
    :ivar final: Fecha de devolución del préstamo.
    """

    nombre = models.CharField(blank=False, null=False, max_length=250, verbose_name='Nombre Producción')
    prestatario = models.OneToOneField(to=User, on_delete=models.CASCADE)
    lugar = models.CharField(default=Ubicacion.CAMPUS, choices=Ubicacion.choices, max_length=2, verbose_name='Lugar de la Producción')
    descripcion_lugar = models.CharField(blank=False, null=True, max_length=125, verbose_name='Lugar Específico')
    descripcion = models.TextField(blank=False, max_length=512, verbose_name='Descripción de la Producción', default="")
    materia = models.ForeignKey(to=Materia, on_delete=models.DO_NOTHING)
    inicio = models.DateTimeField(default=timezone.now, null=False)
    final = models.DateTimeField(default=timezone.now, null=False)
    _articulos = models.ManyToManyField(to='Articulo', through='ArticuloCarrito', blank=True)
    _corresponsables = models.ManyToManyField(to='Prestatario', blank=True, related_name='corresponsables_carrito')

    def eliminar_articulo(self, articulo: 'Articulo', unidades: int = None):
        """
        Elimina un artículo del carrito o reduce su cantidad.

        :param articulo: El artículo que se va a eliminar.
        :param unidades: Unidades que se van a eliminar del artículo. Si es None, se elimina el artículo completamente.
        """
        articulo_carrito = ArticuloCarrito.objects.get(propietario=self, articulo=articulo)
        if unidades is None or unidades >= articulo_carrito.unidades:
            articulo_carrito.delete()
        else:
            articulo_carrito.unidades -= unidades
            articulo_carrito.save()

    def agregar(self, articulo: 'Articulo', unidades: int):
        """
        Agrega un artículo al carrito.

        :param articulo: El artículo que se va a agregar.
        :param unidades: Unidades que se van a agregar del artículo.
        """
        articulo_carrito, created = ArticuloCarrito.objects.get_or_create(propietario=self, articulo=articulo)
        if not created:
            articulo_carrito.unidades += unidades
        else:
            articulo_carrito.unidades = unidades
        articulo_carrito.save()

    def articulos_carrito(self) -> QuerySet['ArticuloCarrito']:
        """
        Obtiene los artículos en el carrito.

        :returns: Lista de artículos en el carrito.
        """
        return ArticuloCarrito.objects.filter(propietario=self)

    def eliminar(self):
        """
        Elimina el carrito.
        """
        self.delete()

    def vacio(self) -> bool:
        """
        Verifica si el carrito está vacío.

        :returns: True si el carrito está vacío, False en caso contrario.
        """
        return self.articulos().count() == 0

    def numero_articulos(self) -> int:
        """
        Obtiene el número de artículos en el carrito.

        :returns: Número de artículos en el carrito.
        """
        return ArticuloCarrito.objects.filter(propietario=self).count()

    def articulos(self) -> QuerySet['Articulo']:
        """
        Obtiene los objetos Articulo que hay en el carrito.

        :returns: Lista de artículos en el carrito.
        """
        return self._articulos.all()

    def ordenar(self) -> bool:
        """
        Convierte el carrito en una orden (transacción).

        :returns: True si la transacción fue exitosa, False en caso contrario.
        """
        try:
            with transaction.atomic():
                orden = Orden.objects.create(
                    nombre=self.nombre,
                    prestatario=self.prestatario,
                    lugar=self.lugar,
                    descripcion_lugar=self.descripcion_lugar,
                    materia=self.materia,
                    inicio=self.inicio,
                    final=self.final,
                    descripcion=self.descripcion
                )

                orden.agregar_corresponsable(self.prestatario)

                for corresponsable in self._corresponsables.all():
                    orden.agregar_corresponsable(corresponsable)

                if self.vacio():
                        raise Exception("No selecciono ningún artículo")
                    
                for articulo_carrito in self.articulos_carrito():
                    unidades = articulo_carrito.articulo.disponible(self.inicio, self.final)
                    len_unidades = len(unidades)

                    if len_unidades < articulo_carrito.unidades:
                        raise Exception("No hay suficientes unidades disponibles")

                    unidades.order_by('?')
                    for i in range(0, articulo_carrito.unidades):
                        orden.agregar_unidad(unidades[i])

                self.delete()
        except Exception as e:
            print(f"Hubo un error, la transacción ha sido cancelada. {str(e)}")
            return False
        return True

    def corresponsables(self) -> QuerySet['Prestatario']:
        """
        Obtiene la lista de corresponsables del carrito.

        :returns: Lista de corresponsables del carrito.
        """
        return self._corresponsables.all()

    def agregar_corresponsable(self, prestatario: 'Prestatario'):
        """
        Agrega un corresponsable al carrito.

        :param prestatario: El prestatario que se quiere agregar como corresponsable.
        """
        self._corresponsables.add(prestatario)


class Reporte(models.Model):
    """
    Representa un reporte a una Orden.

    :param emisor: Usuario que emitió el reporte.
    :param orden: Orden a la que se refiere el reporte.
    :param estado: Estado del reporte.
    :param descripcion: Información adicional del reporte.
    :param emision: Fecha de emisión del reporte.
    """

    class Estado(models.TextChoices):
        ACTIVO = "AC", _("ACTIVO")
        INACTIVO = "IN", _("INACTIVO")

    emisor = models.ForeignKey(to=User, on_delete=models.CASCADE)
    orden = models.OneToOneField(to=Orden, on_delete=models.CASCADE, related_name='reportes')
    estado = models.CharField(max_length=2, choices=Estado.choices, default=Estado.ACTIVO)
    descripcion = models.TextField(null=True, blank=True, max_length=250)
    emision = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.orden}"


class Categoria(models.Model):
    """
    Representa una categoría de artículos.

    :ivar nombre: Nombre de la categoría.
    """

    nombre = models.CharField(primary_key=True, max_length=250)

    def articulos(self) -> QuerySet['Articulo']:
        """
        Obtiene los artículos que pertenecen a esta categoría.

        :returns: Lista de artículos que pertenecen a la categoría.
        """
        return self.articulo_set.all()

    def agregar(self, articulo: 'Articulo'):
        """
        Agrega un artículo a la categoría.

        :param articulo: El artículo que se quiere agregar.
        """
        self.articulo_set.add(articulo)

    def __str__(self):
        return f"{self.nombre}"


class Entrega(models.Model):
    """
    Representa una entrega de equipo al prestatario.

    :param entregador: Usuario encargado de la entrega.
    :param orden: Orden que se entrega.
    :param emision: Fecha de emisión de la entrega.
    """

    orden = models.OneToOneField(to=Orden, on_delete=models.CASCADE, primary_key=True)
    entregador = models.ForeignKey(to=User, on_delete=models.CASCADE)
    emision = models.DateTimeField(auto_now_add=True)


class Devolucion(models.Model):
    """
    Representa una devolución de equipo al Almacén.

    :ivar orden: Orden que se devuelve.
    :ivar almacen: Usuario responsable del Almacén.
    :ivar emision: Fecha de emisión de la devolución.
    """

    orden = models.OneToOneField(to=Orden, on_delete=models.CASCADE, primary_key=True)
    almacen = models.OneToOneField(to=Almacen, on_delete=models.CASCADE)
    emision = models.DateTimeField(auto_now_add=True)


# Autorizaciones

class AutorizacionEstado(models.TextChoices):
    """
    Opciones para el estado de una autorización.
    """
    PENDIENTE = "PN", _("Pendiente")
    RECHAZADA = "RE", _("Rechazada")
    ACEPTADA = "AC", _("Aceptada")


class Autorizacion(models.Model):
    """
    Clase abstracta para representar una autorización.

    :ivar orden: Orden asociada a la autorización.
    :ivar autorizador: Usuario que autoriza la orden.
    :ivar estado: Estado de la autorización.
    """

    class Meta:
        abstract = True

    orden = models.ForeignKey(to=Orden, on_delete=models.CASCADE)
    autorizador = models.ForeignKey(to=User, on_delete=models.CASCADE)
    estado = models.CharField(default=AutorizacionEstado.PENDIENTE, choices=AutorizacionEstado.choices, max_length=2)

    def esta_pendiente(self) -> bool:
        """
        Verifica si la autorización está pendiente.

        :returns: True si la autorización está pendiente, False en caso contrario.
        """
        return self.estado == AutorizacionEstado.PENDIENTE

    def aceptada(self) -> bool:
        """
        Verifica si la autorización ha sido aceptada.

        :returns: True si la autorización ha sido aceptada, False en caso contrario.
        """
        return self.estado == AutorizacionEstado.ACEPTADA

    def rechazada(self) -> bool:
        """
        Verifica si la autorización ha sido rechazada.

        :returns: True si la autorización ha sido rechazada, False en caso contrario.
        """
        return self.estado == AutorizacionEstado.RECHAZADA

    def aceptar(self):
        """
        Acepta la autorización.
        """
        self.estado = AutorizacionEstado.ACEPTADA
        self.save()

    def rechazar(self):
        """
        Rechaza la autorización.
        """
        self.estado = AutorizacionEstado.RECHAZADA
        self.save()


class AutorizacionOrden(Autorizacion):
    """
    Representa una autorización de orden.

    :ivar tipo: Tipo de la orden.
    """

    class Meta:
        verbose_name_plural = "Autorizaciones"
        unique_together = ('orden', 'autorizador')

    tipo = models.CharField(default=TipoOrden.ORDINARIA, choices=TipoOrden.choices, max_length=2)

    def __str__(self):
        return f"({self.get_tipo_display()}) {self.orden}"


class CorresponsableOrden(Autorizacion):
    """
    Representa un corresponsable de una orden.

    :ivar prestatario: Usuario que acepta ser corresponsable.
    :ivar orden: Orden de la que el prestatario es corresponsable.
    """

    class Meta:
        unique_together = ('orden', 'autorizador')


# Clases de relación

class ArticuloCarrito(models.Model):
    """
    Relación entre un Artículo y un Carrito.

    :ivar propietario: Carrito propietario del artículo.
    :ivar articulo: Artículo que se encuentra en el carrito.
    :ivar unidades: Número de unidades del artículo.
    """

    propietario = models.ForeignKey(to=Carrito, on_delete=models.CASCADE, null=True)
    articulo = models.ForeignKey(to=Articulo, on_delete=models.CASCADE)
    unidades = models.IntegerField(default=0)

    def __str__(self):
        return f"({self.unidades}) {self.articulo}"
