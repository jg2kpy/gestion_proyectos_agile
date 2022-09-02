from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from .views import agregar_miembro_proyecto, agregar_rol_usuario, eliminar_miembro_proyecto, eliminar_rol_usuario

urlpatterns = [
    path('eliminar_miembro_proyecto/', eliminar_miembro_proyecto, name="eliminar_miembro_proyecto"),
    path('agregar_a_proyecto/', agregar_miembro_proyecto, name="agregar_usuario_proyecto"),
    path('eliminar_rol_usuario/', eliminar_rol_usuario, name="eliminar_rol_usuario"),
    path('agregar_rol_usuario', agregar_rol_usuario, name="agregar_rol_usuario")
]
