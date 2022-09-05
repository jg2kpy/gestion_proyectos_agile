from django.db import models
from proyectos.models import Proyecto, Sprint
from usuarios.models import Usuario


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

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['nombre', 'proyecto'],
                                    name='constraint_etapa_historia_usuario_nombre_proyecto')
        ]

    def __str__(self):
        """
        Representación en string de la etapa.

        Returns:
            str: Nombre de la etapa.
        """
        return self.nombre


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
    proyecto = models.ForeignKey(Proyecto, related_name='tiposHistoriaUsuario', on_delete=models.CASCADE)
    etapas = models.ManyToManyField(EtapaHistoriaUsuario, blank=True)

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
    """
    nombre = models.CharField(max_length=255)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    subido_por = models.ForeignKey(Usuario, related_name='archivos', null=True, on_delete=models.SET_NULL)

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
    """
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    sprint = models.ForeignKey(Sprint, related_name='historias', on_delete=models.PROTECT)
    etapa = models.ForeignKey(EtapaHistoriaUsuario, related_name='historias', on_delete=models.PROTECT)
    tipo = models.ForeignKey(TipoHistoriaUsusario, related_name='historias', on_delete=models.PROTECT)
    versionPrevia = models.ForeignKey('HistoriaUsuario', related_name='versionSiguiente',
                                      blank=True, null=True, on_delete=models.PROTECT)
    up = models.IntegerField(blank=False)
    bv = models.IntegerField(blank=False)
    usuarioAsignado = models.ForeignKey('usuarios.Usuario', related_name='usuarioAsignado',
                                        blank=True, null=True, on_delete=models.SET_NULL)
    proyecto = models.ForeignKey(Proyecto, related_name='backlog', on_delete=models.PROTECT)
    archivo = models.ManyToManyField(ArchivoAnexo, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['nombre', 'proyecto'], name='constraint_historia_usuario_nombre_proyecto')
        ]

    def __str__(self):
        """
        Representación en string de la historia de usuario.

        Returns:
            str: Nombre de la historia de usuario.
        """
        return self.nombre


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
    historiaUsuario = models.ForeignKey(HistoriaUsuario, related_name='comentarios', on_delete=models.CASCADE)

    def __str__(self):
        """
        Representación en string del comentario.

        Returns:
            str: Contenido del comentario.
        """
        return self.contenido
