from django.db import models


class Proyecto(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    rol = models.ManyToManyField('Rol', blank=True)
    usuario = models.ManyToManyField('Usuario', related_name="equipo", blank=True)
    scrumMaster = models.ForeignKey('Usuario', related_name='scrumMaster')
    estado = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nombre


class Sprint(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    fecha_inicio = models.DateTimeField(blank=True, null=True)
    fecha_fin = models.DateTimeField(blank=True, null=True)
    proyecto = models.ForeignKey(Proyecto, related_name='sprints')
    estado = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nombre
