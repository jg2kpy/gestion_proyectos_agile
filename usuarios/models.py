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
    """
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    username = NULL
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
        return self.email


class RolProyecto(models.Model):
    """
    Roles de usuario que estos tienen en un proyecto específico.
    """
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    usuario = models.ManyToManyField(Usuario, blank=True, related_name="roles_proyecto")
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, null=True, related_name='proyecto_rol')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['nombre', 'proyecto'], name='constraint_rol_nombre_proyecto')
        ]

    def __str__(self):
        return f'{self.nombre} - {self.proyecto}'


class RolSistema(models.Model):
    """
    Roles de usuario que estos tienen en todo el sistema.
    """
    nombre = models.CharField(max_length=255, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    usuario = models.ManyToManyField(Usuario, blank=True, related_name="roles_sistema")

    def __str__(self):
        return self.nombre


class PermisoProyecto(models.Model):
    """
    Permisos de usuario con alcanze proyectos.
    """
    nombre = models.CharField(max_length=255, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    rol = models.ManyToManyField(RolProyecto, blank=True, related_name='roles')

    def __str__(self):
        return self.nombre


class PermisoSistema(models.Model):
    """
    Permisos de usuario con alcanze sistema.
    """
    nombre = models.CharField(max_length=255, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    rol = models.ManyToManyField(RolSistema, blank=True, related_name='roles')

    def __str__(self):
        return self.nombre


@receiver(post_save, sender=Usuario)
def crear_primer_admin(sender, instance, **kwargs):
    """
    Detecta si no existe un administrador en el sistema y en este caso registra como admin al primer usuario en ingresar.
    """
    rol_admin, created = RolSistema.objects.get_or_create(nombre='gpa_admin')
    if created or Usuario.objects.filter(roles_sistema__id=rol_admin.id).count() == 0:
        if created:
            # Agregar permisos de administrador y descripcion
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
    """
    if sociallogin.account.provider == 'github':
        user.github_perfil = sociallogin.account.extra_data['html_url']
        user.avatar_url = sociallogin.account.extra_data['avatar_url']
        user.direccion = sociallogin.account.extra_data['location']

    user.save()
