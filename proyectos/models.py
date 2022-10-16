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
    """
    fecha_inicio = models.DateTimeField(blank=True, null=True)
    fecha_fin = models.DateTimeField(blank=True, null=True)
    proyecto = models.ForeignKey(Proyecto, related_name='sprints', on_delete=models.PROTECT)
    estado = models.CharField(max_length=255, blank=True, null=True)
    duracion = models.IntegerField(blank=False, null=False, validators=[
                             MaxValueValidator(365), MinValueValidator(1)])
    nombre = models.CharField(max_length=255, blank=False, null=False)
    descripcion = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['fecha_inicio', 'proyecto'], name='constraint_sprint_fecha_inicio_proyecto')
        ]

    def __str__(self):
        return self.estado

class UsuarioTiempoEnSprint(models.Model):
    sprint = models.ForeignKey(Sprint, related_name="participantes", on_delete=models.PROTECT)
    usuario = models.ForeignKey('usuarios.Usuario', related_name='sprints', on_delete=models.PROTECT)
    horas = models.IntegerField(blank=False, null=False, validators=[
                             MaxValueValidator(24), MinValueValidator(1)])
    

class Feriado(models.Model):

    proyecto = models.ForeignKey('proyectos.Proyecto', related_name="feriados", on_delete=models.PROTECT)
    descripcion = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(blank=True, null=True)
