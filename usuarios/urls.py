from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from .views import vista_equipo

urlpatterns = [
    path('equipo/', vista_equipo, name='vista_equipo'),
]
