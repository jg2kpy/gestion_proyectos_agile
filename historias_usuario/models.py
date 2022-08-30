from django.db import models
from proyectos.models import Proyecto, Sprint
from usuarios.models import Usuario


class EtapaHistoriaUsuario(models.Model):
    """
    Etapas de historias de usuario, cada una se muestra como una columna en el tablero de la historia de usuario correspondiente.
    """
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    proyecto = models.ForeignKey(Proyecto, related_name='etapasHistoriaUsuario', on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['nombre', 'proyecto'],
                                    name='constraint_etapa_historia_usuario_nombre_proyecto')
        ]

    def __str__(self):
        return self.nombre


class TipoHistoriaUsusario(models.Model):
    """
    Un tipo de historia de usuario. Cada tipo esta relacionado con un proyecto.
    Se pueden importar en otros proyectos.
    """
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    proyecto = models.ForeignKey(Proyecto, related_name='tiposHistoriaUsuario', on_delete=models.CASCADE)
    etapas = models.ManyToManyField(EtapaHistoriaUsuario, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['nombre', 'proyecto'],
                                    name='constaint_tipo_historia_usuario_nombre_proyecto')
        ]

    def __str__(self):
        return self.nombre


class ArchivoAnexo(models.Model):
    """
    Archivos anexos a una historia de usuario.
    El nombre del archivo en el servidor es la comcatenacion del nombe y el id del archivo (nombre_id).
    """
    nombre = models.CharField(max_length=255)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    subido_por = models.ForeignKey(Usuario, related_name='archivos', null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.nombre}_{self.id}'


class HistoriaUsuario(models.Model):
    """
    Cada historia de usuario representa un trabajo a realizar.
    Debe tener UserPoints (up) y BuisnessValue (bv). Se guarda un historial completo.
    """
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    sprint = models.ForeignKey(Sprint, related_name='historias', on_delete=models.PROTECT)
    etapa = models.ForeignKey(EtapaHistoriaUsuario, related_name='historias', on_delete=models.PROTECT)
    tipo = models.ForeignKey(TipoHistoriaUsusario, related_name='historias', on_delete=models.PROTECT)
    versionPrevia = models.ForeignKey('HistoriaUsuario', related_name='versionPrevia',
                                      blank=True, null=True, on_delete=models.PROTECT)
    up = models.IntegerField(blank=False)
    bv = models.IntegerField(blank=False)
    usuarioAsignado = models.ForeignKey('Usuario', related_name='usuarioAsignado',
                                        blank=True, null=True, on_delete=models.SET_NULL)
    proyecto = models.ForeignKey(Proyecto, related_name='backlog', on_delete=models.PROTECT)
    archivo = models.ManyToManyField(ArchivoAnexo, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['nombre', 'proyecto'], name='constraint_historia_usuario_nombre_proyecto')
        ]

    def __str__(self):
        return self.nombre


class Comentario(models.Model):
    """
    Comentario en una historia de usuario.
    """
    contenido = models.TextField(blank=True, null=True)
    usuario = models.ForeignKey('Usuario', related_name='comentarios', null=True, on_delete=models.SET_NULL)
    historiaUsuario = models.ForeignKey(HistoriaUsuario, related_name='comentarios', on_delete=models.CASCADE)

    def __str__(self):
        return self.descripcion
