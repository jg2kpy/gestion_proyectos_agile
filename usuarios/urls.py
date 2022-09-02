from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from .views import agregar_a_proyecto, asignar_rol_proyecto, eliminar_de_proyecto, eliminar_rol_proyecto

urlpatterns = [
    path('agregar_a_proyecto/', agregar_a_proyecto, name="agregar_a_proyecto"),
    path('eliminar_de_proyecto/', eliminar_de_proyecto,name="eliminar_de_proyecto"),
    path('asignar_rol_proyecto', asignar_rol_proyecto, name="asignar_rol_proyecto"),
    path('eliminar_rol_proyecto/', eliminar_rol_proyecto,name="eliminar_rol_proyecto")
]
