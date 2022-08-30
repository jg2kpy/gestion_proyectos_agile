from django.db import models
from proyectos import Proyecto, Sprint


class EtapaHistoriaUsuario(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    proyecto = models.ForeignKey(Proyecto, related_name='etapasHistoriaUsuario')

    def __str__(self):
        return self.nombre


class TipoHistoriaUsusario(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    proyecto = models.ForeignKey(Proyecto, related_name='tiposHistoriaUsuario')
    etapas = models.ManyToManyField(EtapaHistoriaUsuario, blank=True)

    def __str__(self):
        return self.nombre


class HistoriaUsuario(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    sprint = models.ForeignKey(Sprint, related_name='historias')
    estado = models.CharField(max_length=255, blank=True, null=True)
    versionPrevia = models.ForeignKey('HistoriaUsuario', related_name='versionPrevia', blank=True, null=True)
    up = models.IntegerField(blank=False)
    bv = models.IntegerField(blank=False)
    usuarioAsignado = models.ForeignKey('Usuario', related_name='usuarioAsignado', blank=True, null=True)
    proyecto = models.ForeignKey(Proyecto, related_name='backlog')

    def __str__(self):
        return self.nombre


class Comentario(models.Model):
    contenido = models.TextField(blank=True, null=True)
    usuario = models.ForeignKey('Usuario', related_name='comentarios')
    historiaUsuario = models.ForeignKey(HistoriaUsuario, related_name='comentarios')

    def __str__(self):
        return self.descripcion
