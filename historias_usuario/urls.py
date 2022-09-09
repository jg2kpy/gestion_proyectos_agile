from django.urls import path
from .views import crear_tipoHistoriaUsuario, tiposHistoriaUsario, editar_tipoHistoriaUsuario, borrar_tipoHistoriaUsuario

urlpatterns = [
    path('<int:proyecto_id>/', tiposHistoriaUsario, name='tiposHistoriaUsuario'),
    path('crear/<int:proyecto_id>/', crear_tipoHistoriaUsuario, name='crearTipoHistoriaUsuario'),
    path('editar/<int:proyecto_id>/<int:tipo_id>/', editar_tipoHistoriaUsuario, name='editarTipoHistoriaUsuario'),
    path('borrar/<int:proyecto_id>/<int:tipo_id>/', borrar_tipoHistoriaUsuario, name='borrarTipoHistoriaUsuario'),
]
