from django.urls import path
from .views import crear_tipoHistoriaUsuario, tiposHistoriaUsario

urlpatterns = [
    path('<int:proyecto_id>/', tiposHistoriaUsario, name='TiposHistoriaUsuario'),
    path('crear/<int:proyecto_id>/', crear_tipoHistoriaUsuario, name='Crear Historia Usuario'),
]
