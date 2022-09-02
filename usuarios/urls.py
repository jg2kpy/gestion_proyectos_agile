from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from .views import agregar_miembro_proyecto, asignar_rol_proyecto, eliminar_miembro_proyecto, eliminar_rol_proyecto, get_equipo

urlpatterns = [
    path('equipo/', get_equipo, name='get_equipo'),
    path('agregar_miembro_proyecto/', agregar_miembro_proyecto, name="agregar_miembro_proyecto"),
    path('eliminar_miembro_proyecto/', eliminar_miembro_proyecto,name="eliminar_miembro_proyecto"),
    path('asignar_rol_proyecto', asignar_rol_proyecto, name="asignar_rol_proyecto"),
    path('eliminar_rol_proyecto/', eliminar_rol_proyecto,name="eliminar_rol_proyecto")
]
