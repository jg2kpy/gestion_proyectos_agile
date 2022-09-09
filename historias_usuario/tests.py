from phonenumber_field.modelfields import PhoneNumber
from usuarios.models import RolProyecto, Usuario
from usuarios.views import listar_proyectos, vista_equipo
from proyectos.models import Proyecto
from usuarios.models import RolSistema
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.auth import get_user_model
from django.test.client import RequestFactory
from django.test import TestCase
import os
from django import setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gestion_proyectos_agile.settings")
setup()

# Create your tests here.
