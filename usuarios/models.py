from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group
from django.dispatch import receiver
from django.db.models.signals import post_save
from allauth.account.signals import user_signed_up
from phonenumber_field.modelfields import PhoneNumberField

from proyectos.models import Proyecto
from .manager import CustomUserManager
from django.utils import timezone


class Usuario(AbstractUser):
    """
    Usuario por defecto.
    Similar al usuario de Django, pero con un email en lugar de un username, algunos campos extra y first_name y last_name obligatorios.

    :param email: El email del usuario.
    :type email: str
    :param first_name: El nombre del usuario.
    :type first_name: str
    :param last_name: El apellido del usuario.
    :type last_name: str
    :param direccion: La direccion del usuario.
    :type direccion: str
    :param telefono: El telefono del usuario.
    :type telefono: PhoneNumber
    :param avatar_url: La url del avatar del usuario.
    :type avatar_url: str
    :param date_joined: La fecha de creacion del usuario.
    :type date_joined: datetime

    :param is_active: Campo de Django, ignorado en logicas de negocio.
    :type is_active: bool
    :param is_staff: Campo de Django, ignorado en logicas de negocio.
    :type is_staff: bool
    :param username: Campo de Django, se sobreescribe para que pueda ser nulo, ya que se usa email en lugar de username.
    :type username: str
    """
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, unique=False)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    telefono = PhoneNumberField(blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    avatar_url = models.URLField(blank=True)
    first_name = models.CharField(null=False, blank=False, max_length=100)
    last_name = models.CharField(null=False, blank=False, max_length=100)

    objects = CustomUserManager()

    def __str__(self):
        """Representacion en string del usuario.

        Returns:
            str: El email del usuario.
        """
        return self.email


class RolProyecto(models.Model):
    """
    Roles de usuario que estos tienen en un proyecto específico.

    :param nombre: Nombre del rol.
    :type nombre: str
    :param descripcion: Descripción del rol.
    :type descripcion: str
    :param usuario: Usuarios que tienen el rol.
    :type usuario: List[Usuario]
    :param proyecto: Proyecto al que pertenece el rol.
    :type proyecto: Proyecto
    """
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    usuario = models.ManyToManyField(Usuario, blank=True, related_name="roles_proyecto")
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, null=True, related_name='roles')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['nombre', 'proyecto'], name='constraint_rol_nombre_proyecto')
        ]

    def __str__(self):
        """Representación en string del rol.

        Returns:
            str: El nombre del rol.
        """
        return f'{self.nombre} - {self.proyecto}'


class RolSistema(models.Model):
    """
    Roles de usuario que estos tienen en todo el sistema.

    :param nombre: Nombre del rol.
    :type nombre: str
    :param descripcion: Descripción del rol.
    :type descripcion: str
    :param usuario: Usuarios que tienen este rol.
    :type usuario: List[Usuario]
    """
    nombre = models.CharField(max_length=255, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    usuario = models.ManyToManyField(Usuario, blank=True, related_name="roles_sistema")

    def __str__(self):
        """Representación en string del rol.

        Returns:
            str: El nombre del rol.
        """
        return self.nombre


class PermisoProyecto(models.Model):
    """
    Permisos de usuario con alcanze proyectos.

    :param nombre: Nombre del permiso.
    :type nombre: str
    :param descripcion: Descripción del permiso.
    :type descripcion: str
    :param rol: Roles que tienen el permiso.
    :type rol: List[RolProyecto]
    """
    nombre = models.CharField(max_length=255, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    rol = models.ManyToManyField(RolProyecto, blank=True, related_name='permisos')

    def __str__(self):
        """Representación en string del permiso.

        Returns:
            str: El nombre del permiso.
        """
        return self.descripcion


class PermisoSistema(models.Model):
    """
    Permisos de usuario con alcanze sistema.

    :param nombre: Nombre del permiso.
    :type nombre: str
    :param descripcion: Descripción del permiso.
    :type descripcion: str
    :param rol: Roles que tienen este permiso.
    :type rol: List[RolSistema]
    """
    nombre = models.CharField(max_length=255, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    rol = models.ManyToManyField(RolSistema, blank=True, related_name='permisos')

    def __str__(self):
        """Representación en string del permiso.

        Returns:
            str: El nombre del permiso.
        """
        return self.descripcion


@receiver(post_save, sender=Usuario)
def crear_primer_admin(sender, instance, **kwargs):
    """
    Detecta si no existe un administrador en el sistema y en este caso registra como admin al primer usuario en ingresar.

    :param sender: Clase del modelo que envía la señal.
    :type sender: class
    :param instance: Instancia del modelo que envía la señal.
    :type instance: Usuario
    :param kwargs: Argumentos adicionales, ignorados.
    """
    rol_admin, created = RolSistema.objects.get_or_create(nombre='gpa_admin')
    if created or Usuario.objects.filter(roles_sistema__id=rol_admin.id).count() == 0:
        if created:
            # Reservado en caso de que en el futuro se quiera agregar una permisos especiales al primer admin.
            pass

        instance.roles_sistema.add(rol_admin)


@receiver(user_signed_up)
def populate_profile(sociallogin, user, **kwargs):
    """
    Se llama después de registrar un nuevo usuario por SSO. Se encarga de crear un perfil de usuario con los datos de la cuenta de SSO.
    Los adicionales extraidos son;
    - Link a la cuenta original (GitHub)
    - Link a la imagen de perfil
    - Direccion

    :param sociallogin: Objeto que contiene la información de la cuenta de SSO.
    :type sociallogin: SocialLogin
    :param user: Usuario creado.
    :type user: Usuario
    :param kwargs: Argumentos adicionales, ignorados.
    """
    if sociallogin.account.provider == 'github':
        user.github_perfil = sociallogin.account.extra_data['html_url']
        user.avatar_url = sociallogin.account.extra_data['avatar_url']
        user.direccion = sociallogin.account.extra_data['location']

    user.save()
