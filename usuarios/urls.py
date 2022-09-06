from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from .views import  listar_proyectos, vista_equipo

urlpatterns = [
    path('equipo/', listar_proyectos, name='listar_proyectos'),
    path('equipo/<int:proyecto_id>/', vista_equipo, name='vista_equipo')
]
