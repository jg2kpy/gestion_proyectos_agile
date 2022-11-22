from email.policy import default
from re import L
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

class Proyecto(models.Model):
    """
    Un proyecto consiste de un conjunto de sprints, un equipo de trabajo y un backlog de historias de usuario.
    Cada proyecto debe tener un Scrum Master y el nombre del proyecto debe ser único.

    :param nombre: Nombre del proyecto.
    :type nombre: str
    :param descripcion: Descripción del proyecto.
    :type descripcion: str
    :param fecha_creacion: Fecha de creación del proyecto.
    :type fecha_creacion: datetime
    :param fecha_modificacion: Fecha de modificación del proyecto.
    :type fecha_modificacion: datetime
    :param usuario: Usuarios que pertenecen al proyecto.
    :type usuario: List[Usuario]
    :param estado: Estado del proyecto.
    :type estado: str
    :param scrum_master: Scrum Master del proyecto.
    :type scrum_master: Usuario
    :param minimo_dias_sprint: Minimo de dias para un sprint de este proyecto
    :type minimo_dias_sprint: int
    :param maximo_dias_sprint: Maximo de dias para un sprint de este proyecto
    :type maximo_dias_sprint: int
    """
    nombre = models.CharField(max_length=255, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    usuario = models.ManyToManyField('usuarios.Usuario', related_name="equipo", blank=True)
    scrumMaster = models.ForeignKey('usuarios.Usuario', related_name='scrumMaster', on_delete=models.PROTECT)
    estado = models.CharField(max_length=255, blank=True, null=True)
    minimo_dias_sprint = models.IntegerField(default=15)
    maximo_dias_sprint = models.IntegerField(default=30)

    def __str__(self):
        return self.nombre


class ArchivoBurndown(models.Model):
    """
    Archivos pertenecientes al Burndown Chart de cada Sprint terminado.
    El nombre del archivo en el servidor es la concatenación del nombre de Proyecto y nombre de Sprint
    con su respectivo id.

    :param nombre: Nombre del archivo.
    :type nombre: str
    :param fecha_subida: Fecha de subida del archivo.
    :type fecha_subida: datetime
    :param archivo: Archivo perteneciente al Burndown Chart.
    :type archivo: FileField
    """
    nombre = models.CharField(max_length=255)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    archivo = models.FileField(upload_to=f"app/staticfiles/", null=True)

class ArchivoVelocity(models.Model):
    """
    Archivos pertenecientes al Velocity Chart de cada Sprint terminado.
    El nombre del archivo en el servidor es la concatenación del nombre de Proyecto y nombre de Sprint
    con su respectivo id.

    :param nombre: Nombre del archivo.
    :type nombre: str
    :param fecha_subida: Fecha de subida del archivo.
    :type fecha_subida: datetime
    :param proyecto: Proyecto perteneciente al Velocity Chart.
    :type proyecto: Proyecto
    :param archivo: Archivo perteneciente al Velocity Chart.
    :type archivo: FileField
    """
    nombre = models.CharField(max_length=255)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    proyecto = models.OneToOneField(Proyecto, related_name="velocityChart", on_delete=models.PROTECT, null=True)
    archivo = models.FileField(upload_to=f"app/staticfiles/", null=True)
    

class Sprint(models.Model):
    """
    Un Sprint es un periodo de tiempo en el que se puede trabajar en un proyecto sobre un conjunto de historias de usuario.
    Para un Proyecto existe se puede tener solo un Sprint activo a la vez y por lo tanto la combinación de fecha inicio y proyecto debe ser única.

    :param fecha_inicio: Fecha de inicio del sprint.
    :type fecha_inicio: datetime
    :param fecha_fin: Fecha de fin del sprint.
    :type fecha_fin: datetime
    :param proyecto: Proyecto al que pertenece el sprint.
    :type proyecto: Proyecto
    :param estado: Estado del sprint.
    :type estado: str
    :param duracion: Duración del sprint en días.
    :type duracion: int
    :param nombre: Nombre del sprint.
    :type nombre: str
    :param descripcion: Descripción del sprint.
    :type descripcion: str
    :param burndownChart: Archivo referente al burndown chart.
    :type burndownChart: ArchivoBurndown
    """
    fecha_inicio = models.DateTimeField(blank=True, null=True)
    fecha_fin = models.DateTimeField(blank=True, null=True)
    proyecto = models.ForeignKey(Proyecto, related_name='sprints', on_delete=models.PROTECT)
    estado = models.CharField(max_length=255, blank=True, null=True)
    duracion = models.IntegerField(blank=False, null=False, validators=[
                             MaxValueValidator(365), MinValueValidator(1)])
    nombre = models.CharField(max_length=255, blank=False, null=False)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    burndownChart = models.OneToOneField(ArchivoBurndown, related_name='sprint', on_delete=models.DO_NOTHING, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['fecha_inicio', 'proyecto'], name='constraint_sprint_fecha_inicio_proyecto')
        ]

    def __str__(self):
        return self.nombre

    def reemplazar_miembro(self, usuario, nuevo_usuario):
        """
        Reemplaza un miembro del equipo de un sprint por otro.

        :param usuario: Miembro a reemplazar.
        :type usuario: Usuario
        :param nuevo_usuario: Nuevo miembro.
        :type nuevo_usuario: Usuario

        :return: True si el reemplazo se realizó con éxito, False en caso contrario.
        """
        if not self.proyecto.usuario.all().filter(id=usuario.id).exists():
            return (False, "El usuario a reemplazar no pertenece al proyecto")
        if not self.proyecto.usuario.all().filter(id=nuevo_usuario.id).exists():
            return (False, "El nuevo usuario no pertenece al proyecto")
        if usuario == self.proyecto.scrumMaster:
            return (False, "El usuario a reemplazar es el Scrum Master")
        if self.participantes.filter(usuario=nuevo_usuario).exists():
            return (False, "El nuevo usuario ya es parte del Sprint")
        if self.participantes.filter(usuario=usuario).exists():
            historias = self.historias.filter(usuarioAsignado=usuario)
            for historia in historias:
                historia.usuarioAsignado = nuevo_usuario
                historia.save()
            tiempoEnSprint = self.participantes.get(usuario=usuario)
            tiempoEnSprint.usuario = nuevo_usuario
            tiempoEnSprint.save()
            return (True, "El reemplazo se realizó con éxito")
        else:
            return (False, "El usuario a reemplazar no forma parte del Sprint")

class UsuarioTiempoEnSprint(models.Model):
    sprint = models.ForeignKey(Sprint, related_name="participantes", on_delete=models.PROTECT)
    usuario = models.ForeignKey('usuarios.Usuario', related_name='sprints', on_delete=models.PROTECT)
    horas = models.IntegerField(blank=False, null=False, validators=[
                             MaxValueValidator(24), MinValueValidator(0)])
    

class Feriado(models.Model):
    """
    Es aquel que no es día laborable (en el ámbito laboral) o que no es día hábil (en el ámbito procesal)

    :param proyecto: Proyecto del cual pertenece este feriado.
    :type proyecto: Proyecto
    :param descripcion: Descripcion de este feriado.
    :type descripcion: datetime
    :param fecha: Fecha del feriado.
    :type fecha: Fecha
    """
    proyecto = models.ForeignKey(Proyecto, related_name="feriados", on_delete=models.DO_NOTHING)
    descripcion = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(blank=True, null=True)
