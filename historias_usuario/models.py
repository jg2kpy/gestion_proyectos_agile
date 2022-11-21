from email.policy import default
from django.db import models
from django.utils.translation import gettext_lazy as _

from proyectos.models import Proyecto, Sprint
from usuarios.models import Usuario
from django.utils import timezone
from django.utils.timezone import now
from django.core.validators import MaxValueValidator, MinValueValidator


class TipoHistoriaUsusario(models.Model):
    """
    Un tipo de historia de usuario. Cada tipo esta relacionado con un proyecto.
    Se pueden importar en otros proyectos.

    :param nombre: Nombre del tipo de historia de usuario.
    :type nombre: str
    :param descripcion: Descripción del tipo de historia de usuario.
    :type descripcion: str
    :param proyecto: Proyecto al que pertenece el tipo de historia de usuario.
    :type proyecto: Proyecto
    :param etapas: Etapas de la historia de usuario.
    :type etapas: List[EtapaHistoriaUsuario]
    """
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    proyecto = models.ForeignKey(Proyecto, related_name='tiposHistoriaUsuario', on_delete=models.CASCADE, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['nombre', 'proyecto'],
                                    name='constaint_tipo_historia_usuario_nombre_proyecto')
        ]

    def __str__(self):
        """
        Representación en string del tipo de historia de usuario.

        Returns:
            str: El nombre del tipo de historia de usuario.
        """
        return self.nombre


class EtapaHistoriaUsuario(models.Model):
    """
    Etapas de historias de usuario, cada una se muestra como una columna en el tablero de la historia de usuario correspondiente.

    :param nombre: Nombre de la etapa.
    :type nombre: str
    :param descripcion: Descripción de la etapa.
    :type descripcion: str
    :param orden: El número de la etapa en la historia de usuario
    :type orden: int
    """
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    orden = models.IntegerField(blank=False, null=False)
    TipoHistoriaUsusario = models.ForeignKey(TipoHistoriaUsusario, related_name='etapas', on_delete=models.CASCADE)

    def __str__(self):
        """
        Representación en string de la etapa.

        Returns:
            str: Nombre de la etapa.
        """
        return self.nombre


def pathDinamico(instance, filename):
    return 'app/staticfiles/{0}'.format(filename)

class ArchivoAnexo(models.Model):
    """
    Archivos anexos a una historia de usuario.
    El nombre del archivo en el servidor es la comcatenacion del nombe y el id del archivo (nombre_id).

    :param nombre: Nombre del archivo.
    :type nombre: str
    :param fecha_subida: Fecha de subida del archivo.
    :type fecha_subida: datetime
    :param subido_por: Usuario que subió el archivo.
    :type subido_por: Usuario
    :param archivo: Archivo que subió el usuario.
    :type archivo: file
    """
    nombre = models.CharField(max_length=255)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    subido_por = models.ForeignKey(Usuario, related_name='archivos', null=True, on_delete=models.SET_NULL)
    archivo = models.FileField(upload_to=pathDinamico, null=True)

    def __str__(self):
        """
        Representación en string del archivo anexo.

        Returns:
            str: Nombre del archivo anexo en el sistema de archivos del servidor.
        """
        return f'{self.nombre}_{self.id}'


class HistoriaUsuario(models.Model):
    """
    Cada historia de usuario representa un trabajo a realizar.
    Debe tener UserPoints (up) y BuisnessValue (bv). Se guarda un historial completo.

    :param nombre: Nombre de la historia de usuario.
    :type nombre: str
    :param descripcion: Descripción de la historia de usuario.
    :type descripcion: str
    :param fecha_creacion: Fecha de creación de la historia de usuario.
    :type fecha_creacion: datetime
    :param fecha_modificacion: Fecha de modificación de la historia de usuario.
    :type fecha_modificacion: datetime
    :param sprint: Sprint al que pertenece la historia de usuario.
    :type sprint: Sprint
    :param etapa: Etapa actual de la historia de usuario.
    :type etapa: EtapaHistoriaUsuario
    :param tipo: Tipo de la historia de usuario.
    :type tipo: TipoHistoriaUsusario
    :param versionPrevia: Version anterior en el historial.
    :type versionPrevia: HistoriaUsuario
    :param up: UserPoints de la historia de usuario. Entre 1 y 100 inclusivo.
    :type up: int
    :param bv: BuisnessValue de la historia de usuario. Entre 1 y 100 inclusivo.
    :type bv: int
    :param usuarioAsignado: Usuario asignado a la historia de usuario.
    :type usuarioAsignado: Usuario
    :param horasAsignadas: Horas asignadas a la historia de usuario.
    :type horasAsignadas: int
    :param proyecto: Proyecto al que pertenece la historia de usuario.
    :type proyecto: Proyecto
    :param archivo: Archivos anexos a la historia de usuario.
    :type archivo: List[ArchivoAnexo]
    :param sprintInfo: Información de la historia de usuario en un Sprint anterior.
    """
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(default=now)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    sprint = models.ForeignKey(Sprint, related_name='historias', on_delete=models.PROTECT, blank=True, null=True)
    etapa = models.ForeignKey(EtapaHistoriaUsuario, related_name='historias', on_delete=models.PROTECT, blank=True, null=True)
    tipo = models.ForeignKey(TipoHistoriaUsusario, related_name='historias', on_delete=models.PROTECT)
    versionPrevia = models.ForeignKey('HistoriaUsuario', related_name='versionSiguiente',
                                      blank=True, null=True, on_delete=models.PROTECT)
    up = models.IntegerField(blank=False, default=1, validators=[
                             MaxValueValidator(100), MinValueValidator(1)])
    bv = models.IntegerField(blank=False, default=1, validators=[
                             MaxValueValidator(100), MinValueValidator(1)])
    usuarioAsignado = models.ForeignKey('usuarios.Usuario', related_name='usuarioAsignado',
                                        blank=True, null=True, on_delete=models.SET_NULL)
    horasAsignadas = models.IntegerField(blank=False, default=0, validators=[MinValueValidator(0)])

    proyecto = models.ForeignKey(Proyecto, related_name='backlog', on_delete=models.PROTECT)

    class Estado(models.TextChoices):
        ACTIVO = 'A', _('Activo')
        TERMINADO = 'T', _('Terminado')
        CANCELADO = 'C', _('Cancelado')
        HISTORIAL = 'H', _('Historial')
        SNAPSHOT = 'S', _('Snapshot')

    estado = models.CharField(
        max_length=1,
        choices=Estado.choices,
        default=Estado.ACTIVO,
    )
    archivos = models.ManyToManyField(ArchivoAnexo, related_name="historia_usuario", blank=True)

    def getPrioridad(self):
        """
        Obtiene la prioridad de agregar la historia de usuario al sprint.

        params
        """
        # No se puede agregar a nuevos Sprints si la historia esta todavía en un Sprint
        if self.sprint is not None or self.estado != HistoriaUsuario.Estado.ACTIVO:
            return -1
        
        return self.bv * 0.6 + self.up * 0.4 + (30 if len(self.sprintInfo.all()) != 0 else 0)

    
    def guardarConHistorial(self):
        """
        Guarda una copia de la version actual de la historia de usuario en el historial y lo conecta a la version actual.
        Debe ser llamado antes de modificar y guardar la version actual.

        Returns:
            None
        """
        # Clonar y guardar version original para historial
        versionPrevia = HistoriaUsuario.objects.get(id=self.id)
        versionPrevia.pk = None
        versionPrevia.estado = HistoriaUsuario.Estado.HISTORIAL
        versionPrevia.save()
        for archivo in self.archivos.all():
            versionPrevia.archivos.add(archivo)

        for comentario in self.comentarios.all():
            versionPrevia.comentarios.add(comentario)

        self.versionPrevia = versionPrevia
        self.fecha_creacion = timezone.now()
        self.fecha_modificacion = timezone.now()
        self.save()
    
    def restaurarDelHistorial(self, versionPrevia):
        self.guardarConHistorial()
        self.nombre = versionPrevia.nombre
        self.descripcion = versionPrevia.descripcion
        self.bv = versionPrevia.bv
        self.up = versionPrevia.up
        self.usuarioAsignado = versionPrevia.usuarioAsignado
        self.etapa = versionPrevia.etapa

        for comentario in self.comentarios.all():
            self.comentarios.remove(comentario)
        for comentario in versionPrevia.comentarios.all():
            self.comentarios.add(comentario)

        for archivo in self.archivos.all():
            self.archivos.remove(archivo)
        for archivo in versionPrevia.archivos.all():
            self.archivos.add(archivo)
        
        if self.sprint is not None and self.sprint.estado != "Desarrollo" and self.sprint.estado != "Planificado":
            self.sprint = None

        self.save()
    
    def obtenerVersiones(self):
        """
        Retorna la lista de todas las versiones de la US en orden decreciente por fecha.

        Returns:
            List[HistoriaUsuario]: El historial completo en  orden decreciente por fecha.
        """
        versiones = []
        version = self
        while version is not None:
            versiones.append(version)
            version = version.versionPrevia
        return versiones

    def __str__(self):
        """
        Representación en string de la historia de usuario.

        Returns:
            str: Nombre de la historia de usuario.
        """
        return self.nombre


class SprintInfo(models.Model):
    """
    Información de un Sprint anterior de una historia de usuario. Se usa solamente para guardar Info de Sprints anteriores para
    mantener compatabilidad con código viejo.

    :param versionEnHistorial: Historia de usuario en el historial con la cual se dejó de trabajar en el Sprint.
    :type versionEnHistorial: HistoriaUsuario
    :param sprint: Sprint al que pertenece esta informacion.
    :type sprint: Sprint
    :param horasAsignadas: Horas asignadas a la historia de usuario en el Sprint.
    :type horasAsignadas: int
    :param horasUsadas: Horas usadas en el Sprint.
    :type horasUsadas: int
    :param fechaCreacion: Fecha de creación de la información.
    :type fechaCreacion: datetime
    :param historia: Historia de usuario a la que pertenece esta informacion.
    :type historia: HistoriaUsuario
    """

    versionEnHistorial = models.ForeignKey(HistoriaUsuario, on_delete=models.PROTECT)
    historia = models.ForeignKey(HistoriaUsuario, related_name='sprintInfo', on_delete=models.PROTECT)
    sprint = models.ForeignKey(Sprint, related_name="historiasInfo", on_delete=models.PROTECT)
    fechaCreacion = models.DateTimeField(default=timezone.now)
    horasAsignadas = models.IntegerField(blank=False, default=0, validators=[MinValueValidator(0)])
    horasUsadas = models.IntegerField(blank=False, default=0, validators=[MinValueValidator(0)])

class Comentario(models.Model):
    """
    Comentario en una historia de usuario.

    :param historia: Historia de usuario a la que pertenece el comentario.
    :type historia: HistoriaUsuario
    :param usuario: Usuario que hizo el comentario.
    :type usuario: Usuario
    :param contenido: Contenido del comentario.
    :type contenido: str
    """
    contenido = models.TextField(blank=True, null=True)
    usuario = models.ForeignKey('usuarios.Usuario', related_name='comentarios', null=True, on_delete=models.SET_NULL)
    historiaUsuario = models.ManyToManyField(HistoriaUsuario, related_name='comentarios')

    def __str__(self):
        """
        Representación en string del comentario.

        Returns:
            str: Contenido del comentario.
        """
        return self.contenido

class SubirArchivo(models.Model):
    """
    Archivos subidos por el usuario que van a ser anexados

    :param archivo: Archivo que subió el usuario.
    :type archivo: file
    """
    archivo = models.FileField(blank=True, null=True)

class Tarea(models.Model):
    """
    Registra el trabajo realizado por un usuario en una historia de usuario.

    :param historia: Historia de usuario a la que pertenece la tarea.
    :type historia: HistoriaUsuario
    :param usuario: Usuario que realizó la tarea.
    :type usuario: Usuario
    :param fecha: Fecha en la que se realizó la tarea.
    :type fecha: datetime
    :param descripcion: Descripción de la tarea realizada.
    :type descripcion: str
    :param horas: Horas que se trabajaron en la tarea.
    :type horas: int
    :param etapa: Etapa en la que se realizó la tarea.
    :type etapa: Etapa
    :param sprint: Sprint en el que se realizó la tarea.
    :type sprint: Sprint
    """

    fecha = models.DateField(default=timezone.now)
    historia = models.ForeignKey(HistoriaUsuario, related_name='tareas', on_delete=models.PROTECT)
    sprint = models.ForeignKey(Sprint, related_name='tareas', on_delete=models.PROTECT)
    usuario = models.ForeignKey('usuarios.Usuario', related_name='tareas', on_delete=models.PROTECT)
    descripcion = models.TextField(blank=True, null=True)
    etapa = models.ForeignKey(EtapaHistoriaUsuario, related_name='tareas', on_delete=models.PROTECT)
    horas = models.IntegerField(default=0)
    considerado = models.BooleanField(default=False)
