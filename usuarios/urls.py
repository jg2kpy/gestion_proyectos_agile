from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from .views import agregar_mienbro_proyecto, agregar_rol_usuario, eliminar_mienbro_proyecto, eliminar_rol_usuario

urlpatterns = [
    path('eliminar/<proyecto_id>/<usuario_nombre>', eliminar_mienbro_proyecto, name="eliminar_usuario_proyecto"),
    path('agregar_a_proyecto/', agregar_mienbro_proyecto, name="agregar_usuario_proyecto"),
    path('eliminar_rol_usuario/<proyecto_id>/<usuario_nombre>/<rol_id>', eliminar_rol_usuario, name="eliminar_rol_usuario"),
    path('agregar_rol_usuario', agregar_rol_usuario, name="agregar_rol_usuario")
]
