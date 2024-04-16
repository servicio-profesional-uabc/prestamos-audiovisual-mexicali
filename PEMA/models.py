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
    def crear_usuario(*args, **kwargs) -> User:
        """
        Crea un usuario de tipo prestatario, util para hacer pruebas unitarias

        :returns: usuario en el grupo de Prestatarios
        """

        grupo, _ = Prestatario.crear_grupo()
        user = User.objects.create_user(*args, **kwargs)
        grupo.user_set.add(user)

        return user

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
        return Orden.objects.filter(prestatario=self)

    def reportes(self) -> QuerySet['Reporte']:
        """
        Devuelve los reportes del prestatario.

        :returns: Lista de reportes del prestatario.
        """

        return Reporte.objects.filter(orden__in=self.ordenes())

    def materias(self) -> QuerySet['Materia']:
        """
        Devuelve las materias del prestatario.

        :returns: Materias a las que está integrado el prestatario.
        """

        return Materia.objects.filter(usuariomateria__usuario=self)

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
        group.permissions.add(Permission.objects.get(codename='add_devolucion'))
        group.permissions.add(Permission.objects.get(codename='add_entrega'))
        group.permissions.add(Permission.objects.get(codename='add_orden'))
        group.permissions.add(Permission.objects.get(codename='view_orden'))
        group.permissions.add(Permission.objects.get(codename='view_reporte'))

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
    :ivar imagen: Imagen del perfil.
    :ivar telefono: Número de teléfono.
    """

    usuario = models.OneToOneField(to=User, on_delete=models.CASCADE)
    imagen = models.ImageField(default='default.png')
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

    def alumnos(self) -> QuerySet['User']:
        """
        :returns: Lista de alumnos de la materia.
        """
        return User.objects.filter(usuariomateria__materia=self)

    def maestros(self) -> QuerySet['Maestro']:
        """
        :returns: Lista de profesores asociados a la materia.
        """
        return Maestro.objects.filter(maestromateria__materia=self)

    def articulos(self) -> QuerySet['Articulo']:
        """
        :returns: Lista de artículos disponibles para la materia.
        """
        return Articulo.objects.filter(articulomateria__materia=self)

    def agregar_articulo(self, articulo: 'Articulo') -> tuple['ArticuloMateria', bool]:
        """
        :param articulo: Artículo que se quiere agregar.
        :returns: ArticuloMateria agregado y sí se creó el objeto.
        """
        return ArticuloMateria.objects.get_or_create(materia=self, articulo=articulo)

    def agregar_maestro(self, maestro: 'Maestro') -> tuple['MaestroMateria', bool]:
        """
        :param maestro:
        :return:
        """
        return MaestroMateria.objects.get_or_create(maestro=maestro, materia=self)

    def agregar_alumno(self, usuario: 'User') -> tuple['UsuarioMateria', bool]:
        """
        :param usuario: Participante que se agregara como alumno a la Materia.
        :return:
        """
        return UsuarioMateria.objects.get_or_create(usuario=usuario, materia=self)

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
    PENDIENTE_CR = "PC", _("PENDIENTE CORRESPONSABLES")
    PENDIENTE_AP = "PA", _("PENDIENTE APROBACION")
    RECHAZADA = "RE", _("RECHAZADA")
    APROBADA = "AP", _("APROBADA")
    CANCELADA = "CN", _("CANCELADO")


class Orden(models.Model):
    """
    Una orden es un conjunto de Unidades de cada Artículo definido
    el Carrito, para que el encargado del Almacén sepa
    específicamente que entregar.

    .. warning::
        Utilizar ``estado`` unicamente en filtros

    :ivar materia: Materia de la orden.
    :ivar prestatario: Usuario que hace la solicitud.
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
        ordering = ("emision", )
        verbose_name_plural = "Ordenes"

    class Estado(models.TextChoices):
        """
        Opciones para el estado de la orden:
            * PENDIENTE_CR: Esperando confirmación de los corresponsables.
            * PENDIENTE_AP: Esperando aprobación del maestro o coordinador
            * RECHAZADA: Orden rechazada por el maestro o coordinador.
            * APROBADA: Orden aprobada por el maestro o coordinador.
            * CANCELADA: Orden cancelado por el prestatario.
            * CONCLUIDA: Orden que se llevo a cabo sin incidentes de principio a fin.
        """
        PENDIENTE_CR = "PC", _("PENDIENTE CORRESPONSABLES")
        PENDIENTE_AP = "PA", _("PENDIENTE APROBACION")
        RECHAZADA = "RE", _("RECHAZADA")
        APROBADA = "AP", _("APROBADA")
        CANCELADA = "CN", _("CANCELADO")

    class Tipo(models.TextChoices):
        """Opciones para el tipo de orden."""
        ORDINARIA = "OR", _("ORDINARIA")
        EXTRAORDINARIA = "EX", _("EXTRAORDINARIA")

    class Ubicacion(models.TextChoices):
        """Opciones para el lugar de la orden"""
        CAMPUS = "CA", _("CAMPUS")
        EXTERNO = "EX", _("EXTERNO")

    # obligatorio
    nombre = models.CharField(blank=False, max_length=125)
    materia = models.ForeignKey(to=Materia, on_delete=models.DO_NOTHING)
    prestatario = models.ForeignKey(to=Prestatario, on_delete=models.CASCADE)
    inicio = models.DateTimeField(null=False)
    final = models.DateTimeField(null=False)

    # automático
    tipo = models.CharField(default=TipoOrden.ORDINARIA, choices=TipoOrden.choices, max_length=2)
    lugar = models.CharField(default=Ubicacion.CAMPUS, choices=Ubicacion.choices, max_length=2)
    estado = models.CharField(default=EstadoOrden.PENDIENTE_CR, choices=EstadoOrden.choices, max_length=2)
    emision = models.DateTimeField(auto_now_add=True)

    # en caso de que lugar sea Ubicacion.EXTERNO
    descripcion_lugar = models.CharField(blank=False, null=True, max_length=125)

    # opcional
    descripcion = models.TextField(blank=True, max_length=512)

    def es_ordinaria(self) -> bool:
        return self.tipo == TipoOrden.ORDINARIA

    def es_extraordinaria(self):
        return self.tipo == TipoOrden.EXTRAORDINARIA

    def estado_actual(self) -> tuple[bool, str]:
        """
        La función retorna una tupla `(bool, str)`, donde `bool` es
        `True` si la orden puede aprobarse, y en caso contrario, la
        cadena `str` proporciona una explicación del motivo de la no
        aprobación.
        """
        pass

    def unidades(self) -> 'QuerySet[Unidad]':
        """
        Devuelve las unidades con las que se suplió la orden.
        """
        return Unidad.objects.filter(unidadorden__orden=self)

    def articulos(self) -> 'QuerySet[Articulo]':
        """
        Devuelve los artículos en la orden.
        """
        return Articulo.objects.filter(unidad__in=self.unidades())

    def reporte(self) -> 'Reporte':
        """
        Retorna el Reporte de la Orden o nada sí no tiene reporte.

        :returns: Reporte: Reporte asociado a la orden o None si no tiene reporte.
        """
        return Reporte.objects.filter(orden=self).first()

    def agregar_unidad(self, unidad: 'Unidad') -> tuple['UnidadOrden', bool]:
        """
        Agrega una unidad a la orden.

        :param unidad: Unidad que se agregará
        """
        return UnidadOrden.objects.get_or_create(orden=self, unidad=unidad)

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
        return f"{self.nombre}"


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

    prestatario = models.OneToOneField(to=User, on_delete=models.CASCADE)
    materia = models.ForeignKey(to=Materia, on_delete=models.DO_NOTHING)
    inicio = models.DateTimeField(default=timezone.now, null=False)
    final = models.DateTimeField(default=timezone.now, null=False)

    def agregar(self, articulo: 'Articulo', unidades: int = 1) -> tuple['ArticuloCarrito', bool]:
        """
        Agrega un artículo al carrito.

        :param articulo: El artículo que se va a agregar.
        :param unidades: Unidades que se va a agregar del Artículo.

        :returns: Relación al artículo al carrito y si se agregó
        """

        # TODO: falta verificar casos
        # - agregar el mismo articulo otra vez (se suma?)
        # - cambiar el numero de articulos cuando unidades es diferente a 1

        objeto, creado = ArticuloCarrito.objects.get_or_create(articulo=articulo, carrito=self)

        if not creado and objeto.unidades != unidades:
            # Actualizar unidades
            objeto.unidades = unidades
            objeto.save()

        return objeto, creado

    def articulos(self) -> QuerySet['Articulo']:
        """
        Devuelve los artículos en el carrito.

        :returns: Artículos en el carrito.
        """

        return Articulo.objects.filter(articulocarrito__carrito=self)

    def ordenar(self) -> None:
        """
        Convierte el carrito en una orden (Transacción).

        :returns: None
        """

        # TODO: Verificar si la orden es Ordinaria o Extraordinaria

        with transaction.atomic():
            orden = Orden.objects.create(materia=self.materia, prestatario=self.prestatario, inicio=self.inicio,
                                         final=self.final)

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
    codigo = models.CharField(blank=False, null=False, max_length=250)
    descripcion = models.TextField(null=True, blank=True, max_length=250)

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

        """_summary_
        1-Tener lista de ordenes aprobadas de la misma materia que la orden en proceso
        2-Iterar lista de ordenes aprobadas
        3-Comparar conflicto de horarios
        4-Guardar ordenes que tienen conflicto en horario
        TODO:
        5-Iterar lista de ordenes conflicto
        6-Crear lista con la cantidad de unidades de cada articulo en esas ordenes
        7-Restar unidades ocupadas del total de unidades de cada articulo
        8-Regresar lista con unidades libres de cada articulo en el horario solicitado
        
        
        Posibles optimizaciones de momento
        -No utilizar tantas listas
        -Filtrar la mayor cantidad de ordenes con filters para reducir iteraciones del for
        -Buscar mejor combinación de comparaciones de horarios
        
        """

        ordenesAprobadas = Orden.objects.filter(estado=Estado.APROBADA, materia__in=materias(self))
        ordenesConflicto = []
        unidadesConflicto = []
        for ord in ordenesAprobadas.iterator:
            if (ord.inicio == inicio or ord.final == final or (ord.inicio < inicio and ord.final > inicio) or (
                    ord.inicio < final and ord.final > final) or (ord.inicio > inicio and ord.final < final)):
                ordenesConflicto.append(ord)
                unidadesConflicto.append(ord.unidades(ord))

        # unidadesTotales = self.unidades()

        return Unidad.objects.difference(unidadesConflicto)
        # TODO: Me esta volviendo loco este método, lo intentare luego

        pass

    def categorias(self) -> 'QuerySet[Categoria]':
        """
        Devuelve la lista de categorías en las que pertenece el artículo.

        :returns: Categorías a las que pertenece.
        """

        return Categoria.objects.filter(categoriaarticulo__articulo=self)

    def materias(self) -> 'QuerySet[Materia]':
        """
        Lista de materias en las que se encuentra el artículo.

        :returns: Materias asociadas al artículo.
        """

        return Materia.objects.filter(articulomateria__articulo=self)

    def unidades(self) -> 'QuerySet[Unidad]':
        """
        Devuelve la lista de unidades de un artículo.

        :returns: Unidades asociadas al artículo.
        """

        return Unidad.objects.filter(articulo=self)


class Entrega(models.Model):
    """
    Entrega al almacen. Se genera cada vez que Almacen entrega el
    equipo al Prestatario.

    :param almacen: Encargado del Almacen.
    :param orden: Orden que se entrega.
    :param emision: Fecha en la que se hace la emisión.
    """

    orden = models.OneToOneField(to=Orden, on_delete=models.CASCADE, primary_key=True)
    almacen = models.OneToOneField(to=Almacen, on_delete=models.CASCADE)
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


class Unidad(models.Model):
    """
    Clase que representa una unidad de un artículo.

    :ivar articulo: Al que pertenece la unidad
    :ivar estado: De la unidad
    :ivar num_control: Para identificar la unidad
    :ivar num_serie: De la unidad
    """

    class Meta:
        unique_together = ('articulo', 'num_control')

    class Estado(models.TextChoices):
        ACTIVO = "AC", _("ACTIVO")
        INACTIVO = "IN", _("INACTIVO")

    articulo = models.ForeignKey(to=Articulo, on_delete=models.CASCADE)
    estado = models.CharField(max_length=2, choices=Estado.choices, null=False, default=Estado.ACTIVO)
    num_control = models.CharField(max_length=250, null=False, blank=False)
    num_serie = models.CharField(blank=False, null=False, max_length=250)

    def ordenes(self) -> QuerySet[Orden]:
        return Orden.objects.filter(unidadorden__unidad=self)


class Categoria(models.Model):
    """
    Clase que representa una categoría.

    :ivar nombre (str): Nombre de la categoría
    """

    nombre = models.CharField(primary_key=True, max_length=250)

    def articulos(self) -> QuerySet[Articulo]:
        """
        Devuelve los artículos que pertenecen a esta categoría.

        :return: Artículos que pertenecen a la Categoría
        """

        return Articulo.objects.filter(categoriaarticulo__categoria=self)

    def agregar(self, articulo: 'Articulo') -> tuple['CategoriaArticulo', bool]:
        """
        Agrega un Articulo a la Categoría

        :param articulo: Articulo que se agregará

        :returns: CategoriaArticulo y si ha sido creado
        """

        return CategoriaArticulo.objects.get_or_create(categoria=self, articulo=articulo)


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

class ArticuloMateria(models.Model):
    """
    Relación entre un artículo y una materia.

    :ivar articulo: Artículo disponible para la materia.
    :ivar materia: Materia a la que se agrega el artículo.
    """

    class Meta:
        unique_together = ('materia', 'articulo')

    materia = models.ForeignKey(to=Materia, on_delete=models.CASCADE)
    articulo = models.ForeignKey(to=Articulo, on_delete=models.CASCADE)


class ArticuloCarrito(models.Model):
    """
    Relación entre un Artículo y un Carrito.

    :ivar articulo: Artículo que se encuentra en el carrito.
    :ivar carrito: Carrito de un usuario.
    :ivar unidades: Número de unidades que se van a solicitar del artículo.
    """

    class Meta:
        unique_together = ('articulo', 'carrito')

    articulo = models.ForeignKey(to=Articulo, on_delete=models.CASCADE)
    carrito = models.ForeignKey(to=Carrito, on_delete=models.CASCADE)
    unidades = models.IntegerField(default=1, )


class CategoriaArticulo(models.Model):
    """
    Relación entre una Categoría y un Artículo.

    :ivar categoria: Categoría a la que pertenece Artículo.
    :ivar articulo: Artículo que se encuentra en la Categoría.
    """

    class Meta:
        unique_together = ('articulo', 'categoria')

    articulo = models.ForeignKey(to=Articulo, on_delete=models.CASCADE)
    categoria = models.ForeignKey(to=Categoria, on_delete=models.CASCADE)


class UnidadOrden(models.Model):
    """
    Relación entre una unidad y una orden.

    :ivar unidad: Unidad asignada a la orden.
    :ivar orden: Orden a la que se asignan las unidades.
    """

    class Meta:
        unique_together = ('unidad', 'orden')

    unidad = models.ForeignKey(to=Unidad, on_delete=models.CASCADE)
    orden = models.ForeignKey(to=Orden, on_delete=models.CASCADE)


class MaestroMateria(models.Model):
    """
    Relacion entre el maestro y una materia.

    :ivar materia: Materia asignada.
    :ivar maestro: Usuario Maestro.
    """

    class Meta:
        unique_together = ('materia', 'maestro')

    materia = models.ForeignKey(to=Materia, on_delete=models.CASCADE)
    maestro = models.ForeignKey(to=Maestro, on_delete=models.CASCADE)


class UsuarioMateria(models.Model):
    """
    Relación entre el Usuario y la materia.

    :ivar materia: Materia asignada.
    :ivar usuario: Usuario participante.
    """

    class Meta:
        unique_together = ('materia', 'usuario')

    materia = models.ForeignKey(to=Materia, on_delete=models.CASCADE)
    usuario = models.ForeignKey(to=User, on_delete=models.CASCADE)
