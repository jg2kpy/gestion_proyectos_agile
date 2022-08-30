import imp
from statistics import mode
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group
from django.dispatch import receiver
from django.db.models.signals import post_save

from proyectos.models import Proyecto
from .manager import CustomUserManager
from django.utils import timezone


class Usuario(AbstractUser):
    """
    Usuario por defecto.
    """
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Rol(models.Model):
    """
    Roles de usuario.
    """
    nombre = models.CharField(max_length=255, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    usuario = models.ManyToManyField(Usuario, blank=True, related_name="roles")
    proyecto = models.ManyToManyField(Proyecto)

    def __str__(self):
        return self.nombre


class Permiso(models.Model):
    """
    Permisos de usuario.
    """
    nombre = models.CharField(max_length=255, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    rol = models.ManyToManyField(Rol, blank=True, related_name='roles')

    def __str__(self):
        return self.nombre


@receiver(post_save, sender=Usuario)
def crear_primer_admin(sender, instance, **kwargs):
    """
    Detecta si no existe un administrador en el sistema y en este caso registra como admin al primer usuario en ingresar.
    """
    rol_admin, created = Rol.objects.get_or_create(nombre='gpa_admin', proyecto__isnull=True)
    if created or Usuario.objects.filter(roles__id=rol_admin.id).count() == 0:
        if created:
            # Agregar permisos de administrador y descripcion
            pass

        instance.roles.add(rol_admin)
