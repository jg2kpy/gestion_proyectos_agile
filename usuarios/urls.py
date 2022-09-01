from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from .views import eliminar_mienbro_proyecto

urlpatterns = [
    path('eliminar/<proyecto_nombre>/<usuario_nombre>', eliminar_mienbro_proyecto, name="eliminar_usuario"),
]
