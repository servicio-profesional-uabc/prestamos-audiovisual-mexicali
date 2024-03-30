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


class Prestatario(User):
    """
    Es un tipo de usuario con permisos específicos para solicitar
    equipos del almacén y ser corresponsable de órdenes.
    """

    class Meta:
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

        return Materia.objects.filter(materiausuario__usuario=self)

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
        proxy = True

    @classmethod
    def crear_grupo(cls) -> tuple[Any, bool]:
        """
        Crea el grupo de permisos para Coordinadores.

        :returns: Grupo de Coordinadores y si se creó el grupo.
        """

        # grupo
        group, created = Group.objects.get_or_create(name='coordinador')

        # permisos
        group.permissions.add(Permission.objects.get(codename='add_autorizacionextraordinaria'))
        group.permissions.add(Permission.objects.get(codename='delete_orden'))
        group.permissions.add(Permission.objects.get(codename='change_reporte'))

        return group, created

    def autorizar(self, orden: 'Orden') -> tuple['AutorizacionExtraordinaria', bool]:
        """
        Autoriza una orden específica.

        :param orden: Orden que se va a autorizar
        """

        # crear la autorizacion extraordinaria
        autorizacion, created = AutorizacionExtraordinaria.objects.get_or_create(orden=orden, coordinador=self)

        # actualizar el estado de autorizacion
        autorizacion.autorizar = True

        return autorizacion, created


class Maestro(User):
    """
    Un maestro puede autorizar ordenes ordinarias y ser el
    supervisor de una clase.
    """

    class MaestroManager(models.Manager):
        def get_queryset(self, *args, **kwargs):
            return super().get_queryset(*args, **kwargs).filter(groups__name='maestro')

    objects = MaestroManager()

    class Meta:
        proxy = True

    @staticmethod
    def crear_grupo() -> tuple[Any, bool]:
        """
        Crea el 'Permission Group' para el usuario maestro.

        :returns: el grupo y sí se creó
        """

        # grupo
        group, created = Group.objects.get_or_create(name='maestro')

        # permisos
        group.permissions.add(Permission.objects.get(codename='add_autorizacionordinaria'))
        group.permissions.add(Permission.objects.get(codename='change_autorizacionordinaria'))

        return group, created

    def autorizar(self, orden: 'Orden') -> tuple['AutorizacionOrdinaria', bool]:
        """
        Autoriza órdenes ordinarias.

        :param orden: La orden que se va a autorizar.
        :returns: AutorizacionOrdinaria y si se creo
        """

        # TODO: Este metodo esta pediente

        pass

    def materias(self) -> QuerySet['Materia']:
        """
        Materias que supervisa el maestro.

        :returns: Materias supervisadas por el maestro.
        """

        # TODO: este método esta pendiente

        pass


class Almacen(User):
    """
    Clase que representa al usuario Almacén, Un usuario almacen 
    puede surtir las Ordenes de los prestatarios también se encarga 
    de recibir el equipo.
    """

    class AlmacenManager(models.Manager):
        def get_queryset(self, *args, **kwargs):
            return super().get_queryset(*args, **kwargs).filter(groups__name='almacen')

    objects = AlmacenManager()

    class Meta:
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
        """Crea el 'Permission Group' para el usuario almacén.

        :returns: El grupo creado y sí se creo el grupo
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
        """Crea un usuario de tipo prestatario"""

        grupo, _ = Almacen.crear_grupo()
        user = User.objects.create_user(*args, **kwargs)
        grupo.user_set.add(user)

        return user

    def entregar(self, orden: 'Orden') -> tuple['Entrega', bool]:
        """Generar el registro que el Almacén entrego el equipo.

        :param orden: La orden entregada
        :returns: Registro de entrega y si el registro se creó
        """

        return Entrega.objects.get_or_create(almacen=self, orden=orden)

    def devolver(self, orden: 'Orden') -> tuple['Devolucion', bool]:
        """
        Generar el registro que el Almacén recibió el equipo de vuelta.

        :param orden: La orden que se va a devolver.
        :returns: El registro de devolución, si el registro se creó
        """

        return Devolucion.objects.get_or_create(almacen=self, orden=orden)

    def reportar(self, orden: 'Orden', descripcion: str) -> tuple['Reporte', bool]:
        """Reporta una orden.

        :param orden: La orden que se va a reportar.
        :param descripcion: Información adicional del Reporte
        :returns: Reporte y sí el objeto se creó.
        """

        return Reporte.objects.get_or_create(almacen=self, orden=orden, descripcion=descripcion)


class Perfil(models.Model):
    """
    Esta clase proporciona acceso a todos los datos de un usuario.
    Se implementa para evitar complicar el modelo de usuario de
    Django. Además, este método facilita el acceso a los datos que ya
    están incluidos mediante métodos específicos.

    :param usuario: Usuario del perfil
    :param imagen: Imagen del perfil
    :param telefono: Número de teléfono
    """

    usuario = models.OneToOneField(to=User, on_delete=models.CASCADE)
    imagen = models.ImageField(default='default.png')
    telefono = PhoneNumberField(null=True)

    @classmethod
    def user_data(cls, user: User) -> tuple['Perfil', bool]:
        """
        Obtiene el perfil asociado a un usuario.

        :param user: El usuario del cual se desea obtener el perfil.
        :returns: El perfil asociado al usuario.
        """
        return Perfil.objects.get_or_create(usuario=user)

    def email(self):
        """

        :return:
        """


class Orden(models.Model):
    """Clase que representa una orden del almacén.

    Una orden es un conjunto de Unidades de cada Artículo definido
    el Carrito, para que el encargado del Almacén sepa
    específicamente que entregar.

    Attributes:
        prestatario: Usuario que hace la solicitud.
        lugar: Lugar donde se usara el material.
        inicio: Fecha de inicio de la orden.
        final: Fecha de devolución de la orden.
        descripcion: Información adicional de la orden.
        emision: fecha de emisión de la orden.
    """

    class Estado(models.TextChoices):
        """Opciones para el estado de la orden."""
        PENDIENTE = "PN", _("PENDIENTE")
        RECHAZADA = "RE", _("RECHAZADA")
        APROBADA = "AP", _("APROBADA")
        CANCELADO = "CN", _("CANCELADO")

    class Tipo(models.TextChoices):
        """Opciones para el tipo de orden."""
        ORDINARIA = "OR", _("ORDINARIA")
        EXTRAORDINARIA = "EX", _("EXTRAORDINARIA")

    class Ubicacion(models.TextChoices):
        """Opciones para el lugar de la orden"""
        CAPUS = "CA", _("CAPUS")
        EXTERNO = "EX", _("EXTERNO")

    prestatario = models.ForeignKey(to=Prestatario, on_delete=models.CASCADE)
    lugar = models.CharField(default=Ubicacion.CAPUS, choices=Ubicacion.choices, max_length=2)
    inicio = models.DateTimeField(null=False)
    final = models.DateTimeField(null=False)
    emision = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField(blank=True, max_length=512)

    def unidades(self) -> 'QuerySet[Unidad]':
        """Devuelve las unidades con las que se suplió la orden.

        :returns: QuerySet[Unidad]: Unidades asociadas a la orden.
        """

        return Unidad.objects.filter(unidadorden__orden=self)

    def articulos(self) -> 'QuerySet[Articulo]':
        """Devuelve los artículos en la orden.

        :returns: QuerySet[Articulo]: Artículos asociados a la orden.
        """

        return Articulo.objects.filter(unidad__in=self.unidades())

    def reporte(self) -> 'Reporte':
        """Retorna el Reporte de la Orden o nada sí no tiene reporte.

        :returns: Reporte: Reporte asociado a la orden o None si no tiene reporte.
        """

        return Reporte.objects.filter(orden=self).first()

    def estado(self) -> str:
        """
        Devuelve el estado de la Orden.

        :returns: str: Estado de la orden (PENDIENTE, RECHAZADA o APROBADA).
        """
        # TODO: falta implementar este método, Falta acordar detalles
        pass

    def agregar_unidad(self, unidad: 'Unidad') -> tuple['UnidadOrden', bool]:
        """Agrega una unidad especifíca a la orden

         Attributes:
             unidad (Unidad): Unidad que se agregará
        """
        return UnidadOrden.objects.get_or_create(orden=self, unidad=unidad)


class Materia(models.Model):
    """Clase que representa una materia.

    Las materias se encargan de limitar el material al que pueden
    acceder los Prestatarios.

    Attributes:
        nombre (str): Nombre de la clase
        periodo (str): Periodo de la clase ej. 2022-1
    """

    class Meta:
        unique_together = ('nombre', 'periodo')

    nombre = models.CharField(primary_key=True, max_length=250, null=False, blank=False)

    # TODO: separar año y periodo
    periodo = models.CharField(max_length=6, null=False, blank=False)

    @staticmethod
    def alumnos() -> 'QuerySet[User]':
        """Devuelve la lista de alumnos en la clase.

        :returns: QuerySet[User]: Lista de alumnos de la materia.
        """

        return User.objects.exclude(groups__name__in=['coordinador', 'maestro', 'almacen'])

    @staticmethod
    def profesores() -> 'QuerySet[User]':
        """Devuelve la lista de profesores en la clase.

        :returns: QuerySet[User]: Lista de profesores asociados a la materia.
        """

        return User.objects.exclude(groups__name__in=['coordinador', 'prestatarios', 'almacen'])

    def articulos(self) -> 'QuerySet[Articulo]':
        """Artículos que se pueden solicitar.

        :returns: QuerySet[Articulo]: Lista de artículos de la materia.
        """

        return Articulo.objects.filter(articulomateria__materia=self)

    def agregar_articulo(self, articulo: 'Articulo') -> tuple['Articulo', bool]:
        """Agrega un articulo a la lista de equipo disponible para esta materia

         Attribute:
            articulo (Articulo): Articulo que se quiere agregar
        """

        return ArticuloMateria.objects.get_or_create(materia=self, articulo=articulo)

    def agregar_participante(self, usuario: 'User') -> tuple['MateriaUsuario', bool]:
        """Agrega un participante a la clase

        Attribute:
            usuario (User): Participante que se quiere agregar a la clase
        """
        return MateriaUsuario.objects.get_or_create(usuario=usuario, materia=self)


class Carrito(models.Model):
    """Clase que representa un carrito de compras.

    Se usa para seleccionar los artículos del cátalogo, cuando los
    artículos ya se han seleccionado se puede convertir en una Orden.

    Attributes:
       prestatario (Prestatario): Usuario dueño del carrito
       materia (Materia): materia a la que está ligado el equipo del carrito.
       inicio (DateTime): fecha de inicio del préstamo.
       final (DateTime): fecha de devolución del préstamo.
    """

    prestatario = models.OneToOneField(to=User, on_delete=models.CASCADE)
    materia = models.OneToOneField(to=Materia, on_delete=models.DO_NOTHING)
    inicio = models.DateTimeField(default=timezone.now, null=False)
    final = models.DateTimeField(default=timezone.now, null=False)

    def agregar(self, articulo: 'Articulo', unidades: int = 1) -> tuple['ArticuloCarrito', bool]:
        """
        Agrega un artículo al carrito.

        Args:
            articulo: El artículo que se va a agregar.
            unidades: Unidades que se va a agregar del Artículo.

        Return:
            Relación al artículo al carrito y si se agregó
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

    def articulos(self) -> 'QuerySet[Articulo]':
        """Devuelve los artículos en el carrito.

        :returns: [Articulo]: Artículos en el carrito.
        """

        return Articulo.objects.filter(articulocarrito__carrito=self)

    def ordenar(self) -> None:
        """
        Convierte el carrito en una orden (Transacción).

        :returns: None
        """

        # TODO: reimplementar este metodo cuando haya mas detalles
        # TODO: Verificar si la orden es Ordinaria o Extraordinaria
        # TODO: Como identificar el 'lugar' de la orden

        with transaction.atomic():
            Orden.objects.create(prestatario=self.prestatario, inicio=self.inicio, final=self.final)

            # TODO: convertir los ArticuloCarrito a UnidadOrden

            self.delete()


class Reporte(models.Model):
    """Clase que representa un reporte a una Orden.

    Attributes:
        almacen (Almacen): Usuario que emitió el reporte
        orden (Orden): Orden a la que se refiere el reporte
        estado (Estado): Estado de la orden
        descripcion (Descripcion): Información de la orden
        emision (Emision): fecha de emisión del reporte
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
    """Clase que representa un artículo.

    Attributes:
        nombre (str): Nombre
        codigo (str): Identificador
        descripcion (str): Descripción breve
        imagen (Image): Imagen
    """

    class Meta:
        unique_together = ('nombre', 'codigo')

    imagen = models.ImageField(default='default.png')
    nombre = models.CharField(blank=False, null=False, max_length=250)
    codigo = models.CharField(blank=False, null=False, max_length=250)
    descripcion = models.TextField(null=True, blank=True, max_length=250)

    def crear_unidad(self, num_control: str, num_serie: str) -> tuple['Unidad', bool]:
        """registrar una unidad de un articulo

        Attribute:
            num_control (str): numero de control de la unidad
            num_serie (str): numero de series de la unidad
        """

        return Unidad.objects.get_or_create(articulo=self, num_control=num_control, num_serie=num_serie)

    def disponible(self, inicio, final) -> 'QuerySet[Unidad]':
        """Lista con las unidades disponibles en el rango [inicio, final].

        Args:
            inicio (DateTime): Fecha y hora de inicio del rango.
            final (DateTime): Fecha y hora de finalización del rango.

        :returns: QuerySet[Unidad]: Unidades disponibles en el rango especificado.
        """

        # TODO: Me esta volviendo loco este método, lo intentare luego

        pass

    def categorias(self) -> 'QuerySet[Categoria]':
        """Devuelve la lista de categorías en las que pertenece el artículo.

        :returns: QuerySet[Categoria]: Categorías a las que pertenece.
        """

        return Categoria.objects.filter(categoriaarticulo__articulo=self)

    def materias(self) -> 'QuerySet[Materia]':
        """Lista de materias en las que se encuentra el artículo.

        :returns: QuerySet[Materia]: Materias asociadas al artículo.
        """

        return Materia.objects.filter(articulomateria__articulo=self)

    def unidades(self) -> 'QuerySet[Unidad]':
        """Devuelve la lista de unidades de un artículo.

        :returns: QuerySet[Unidad]: Unidades asociadas al artículo.
        """

        return Unidad.objects.filter(articulo=self)


class Entrega(models.Model):
    """Entrega al almacen.

    Se genera cada vez que Almacen entrega el equipo al Prestatario.

    Attributes:
        almacen: encargado del Almacen
        orden: orden que se entrega
        emision: fecha en la que se hace la emisión
    """

    orden = models.OneToOneField(to=Orden, on_delete=models.CASCADE, primary_key=True)
    almacen = models.OneToOneField(to=Almacen, on_delete=models.CASCADE)
    emision = models.DateTimeField(auto_now_add=True)


class Devolucion(models.Model):
    """Devolución del equipo al Almacen

    Se genera cada vez que Prestatario devuelve el equipo al Almacen.

    Attributes:
        orden (Orden): orden que se devuelve
        almacen (Almacen): responsable del almacen
        emision (DateTime): fecha de emisión
    """

    orden = models.OneToOneField(to=Orden, on_delete=models.CASCADE, primary_key=True)
    almacen = models.OneToOneField(to=Almacen, on_delete=models.CASCADE)
    emision = models.DateTimeField(auto_now_add=True)


class Unidad(models.Model):
    """Clase que representa una unidad de un artículo.

    Attributes:
        articulo (Articulo): al que pertenece la unidad
        estado (Estado): de la unidad
        num_control (Str): para identificar la unidad
        num_serie (Str): de la unidad
    """

    class Meta:
        unique_together = ('articulo', 'num_control')

    class Estado(models.TextChoices):
        ACTIVO = "AC", _("ACTIVO")
        INACTIVO = "IN", _("INACTIVO")

    articulo = models.OneToOneField(to=Articulo, on_delete=models.CASCADE)
    estado = models.CharField(max_length=2, choices=Estado.choices, null=False, default=Estado.ACTIVO)
    num_control = models.CharField(max_length=250, null=False, blank=False)
    num_serie = models.CharField(blank=False, null=False, max_length=250)

    def ordenes(self) -> QuerySet[Orden]:
        return Orden.objects.filter(unidadorden__unidad=self)


class Categoria(models.Model):
    """Clase que representa una categoría.

    Attributes:
        nombre (str): Nombre de la categoría
    """

    nombre = models.CharField(primary_key=True, max_length=250)

    def articulos(self) -> QuerySet[Articulo]:
        """Devuelve los artículos que pertenecen a esta categoría.

        Return:
            Artículos que pertenecen a la Categoría
        """

        return Articulo.objects.filter(categoriaarticulo__categoria=self)

    def agregar(self, articulo: 'Articulo') -> tuple['CategoriaArticulo', bool]:
        """Agrega un Articulo a la Categoría

        Args:
            articulo (Articulo): Articulo que se agregará

        Return:
            Relación del Articulo con la Categoría y si el Articulo
            ha sido creado
        """

        return CategoriaArticulo.objects.get_or_create(categoria=self, articulo=articulo)


class AutorizacionOrdinaria(models.Model):
    """Clase que representa una autorización ordinaria.

    Attributes:
        orden (Orden): Orden a la que pertenece la autorización
        maestro (Usuario): Usuario que autoriza la orden
        autorizar (boolean): Estado de la autorización
    """

    class Meta:
        unique_together = ('orden', 'maestro')

    orden = models.OneToOneField(to=Orden, on_delete=models.CASCADE)
    maestro = models.OneToOneField(to=Almacen, on_delete=models.CASCADE)
    autorizar = models.BooleanField(default=False)


class AutorizacionExtraordinaria(models.Model):
    """
    Clase que representa una autorización extraordinaria.
    """

    class Meta:
        unique_together = ('orden', 'coordinador')

    orden = models.OneToOneField(to=Orden, on_delete=models.CASCADE)
    coordinador = models.OneToOneField(to=Coordinador, on_delete=models.CASCADE)
    autorizar = models.BooleanField(default=False)


class CorresponsableOrden(models.Model):
    """Corresponsable de una orden.

    Attributes:
        prestatario: Usuario que acepta ser corresponsable.
        orden: de la que el prestatario es corresponsable.
        aceptado: Si el Prestatario acepto la corresponsabilidad.
    """

    class Meta:
        unique_together = ('orden', 'prestatario')

    prestatario = models.OneToOneField(to=Prestatario, on_delete=models.CASCADE, )
    orden = models.OneToOneField(to=Orden, on_delete=models.CASCADE)
    aceptado = models.BooleanField(default=False, )


class ArticuloMateria(models.Model):
    """Relación entre un artículo y una materia.

    Attributes:
        articulo (Articulo): Artículo disponible para la materia.
        materia (Materia): Materia a la que se agrega el artículo.
    """

    class Meta:
        unique_together = ('materia', 'articulo')

    materia = models.ForeignKey(to=Materia, on_delete=models.CASCADE)
    articulo = models.ForeignKey(to=Articulo, on_delete=models.CASCADE)


class ArticuloCarrito(models.Model):
    """Relación entre un Artículo y un Carrito.

    Attributes:
        articulo (Articulo): Artículo que se encuentra en el carrito.
        carrito (Carrito): Carrito de un usuario.
        unidades (Int): Número de unidades que se van a solicitar del artículo.
    """

    class Meta:
        unique_together = ('articulo', 'carrito')

    articulo = models.ForeignKey(to=Articulo, on_delete=models.CASCADE)
    carrito = models.ForeignKey(to=Carrito, on_delete=models.CASCADE)
    unidades = models.IntegerField(default=1, )


class CategoriaArticulo(models.Model):
    """Relación entre una Categoría y un Artículo.

    Attributes:
        categoria (Categoria): Categoría a la que pertenece Artículo.
        articulo (Articulo): Artículo que se encuentra en la Categoría.
    """

    class Meta:
        unique_together = ('articulo', 'categoria')

    articulo = models.ForeignKey(to=Articulo, on_delete=models.CASCADE)
    categoria = models.ForeignKey(to=Categoria, on_delete=models.CASCADE)


class UnidadOrden(models.Model):
    """Relación entre una unidad y una orden.

    Attributes:
        unidad (Unidad): Unidad asignada a la orden.
        orden (Orden): Orden a la que se asignan las unidades.
    """

    class Meta:
        unique_together = ('unidad', 'orden')

    unidad = models.ForeignKey(to=Unidad, on_delete=models.CASCADE)
    orden = models.ForeignKey(to=Orden, on_delete=models.CASCADE)


class MateriaUsuario(models.Model):
    """Relación entre el Usuario y la materia

    Attributes:
        materia (Materia): Materia asignada
        usuario (Usuario): Usuario participante
    """

    class Meta:
        unique_together = ('materia', 'usuario')

    materia = models.ForeignKey(to=Materia, on_delete=models.CASCADE)
    usuario = models.ForeignKey(to=User, on_delete=models.CASCADE)
