from django.urls import path
from .views import asignarUP_historiaUsuario, borrar_historiaUsuario, crear_historiaUsuario, crear_tipoHistoriaUsuario, historiaUsuario, tiposHistoriaUsuario, editar_tipoHistoriaUsuario, borrar_tipoHistoriaUsuario, importar_tipoUS

urlpatterns = [
    path('tipo-historia-usuario/<int:proyecto_id>/', tiposHistoriaUsuario, name='tiposHistoriaUsuario'),
    path('tipo-historia-usuario/crear/<int:proyecto_id>/', crear_tipoHistoriaUsuario, name='crearTipoHistoriaUsuario'),
    path('tipo-historia-usuario/editar/<int:proyecto_id>/<int:tipo_id>/', editar_tipoHistoriaUsuario, name='editarTipoHistoriaUsuario'),
    path('tipo-historia-usuario/borrar/<int:proyecto_id>/<int:tipo_id>/', borrar_tipoHistoriaUsuario, name='borrarTipoHistoriaUsuario'),
    path('tipo-historia-usuario/importar/<int:proyecto_id>/', importar_tipoUS, name='importarTipoHistoriaUsuario'),

    path('historia-usuario/<int:proyecto_id>/', historiaUsuario, name='historiaUsuario'),
    path('historia-usuario/crear/<int:proyecto_id>/', crear_historiaUsuario, name='crearhistoriaUsuario'),
    path('historia-usuario/borrar/<int:proyecto_id>/<int:historia_id>/', borrar_historiaUsuario, name='borrar_historiaUsuario'),
    path('historia-usuario/asignarUP/<int:proyecto_id>/<int:historia_id>/', asignarUP_historiaUsuario, name='asignarUP_historiaUsuario'),
]
