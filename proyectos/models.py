from django.db import models


class Proyecto(models.Model):
    """
    Un proyecto consiste de un conjunto de sprints, un equipo de trabajo y un backlog de historias de usuario.
    Cada proyecto debe tener un Scrum Master y el nombre del proyecto debe ser único.
    """
    nombre = models.CharField(max_length=255, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    usuario = models.ManyToManyField('Usuario', related_name="equipo", blank=True)
    scrumMaster = models.ForeignKey('Usuario', related_name='scrumMaster')
    estado = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nombre


class Sprint(models.Model):
    """
    Un Sprint es un periodo de tiempo en el que se puede trabajar en un proyecto sobre un conjunto de historias de usuario.
    Para un Proyecto existe se puede tener solo un Sprint activo a la vez y por lo tanto la combinación de fecha inicio y proyecto debe ser única.
    """
    fecha_inicio = models.DateTimeField(blank=True, null=True)
    fecha_fin = models.DateTimeField(blank=True, null=True)
    proyecto = models.ForeignKey(Proyecto, related_name='sprints')
    estado = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['fecha_inicio', 'proyecto'], name='constraint_sprint_fecha_inicio_proyecto')
        ]

    def __str__(self):
        return self.nombre
