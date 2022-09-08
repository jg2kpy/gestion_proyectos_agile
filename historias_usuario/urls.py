from django.urls import path
from .views import crear_tipoHistoriaUsuario

urlpatterns = [
    path('crear/<int:proyecto_id>/', crear_tipoHistoriaUsuario, name='TiposHistoriaUsuario'),
]
