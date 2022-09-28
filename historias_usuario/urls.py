from django.urls import path
from .views import *

urlpatterns = [
    path('<int:proyecto_id>/tipo-historia-usuario/', tiposHistoriaUsuario, name='tiposHistoriaUsuario'),
    path('<int:proyecto_id>/tipo-historia-usuario/crear/', crear_tipoHistoriaUsuario, name='crearTipoHistoriaUsuario'),
    path('<int:proyecto_id>/tipo-historia-usuario/<int:tipo_id>/editar/', editar_tipoHistoriaUsuario, name='editarTipoHistoriaUsuario'),
    path('<int:proyecto_id>/tipo-historia-usuario/<int:tipo_id>/borrar/', borrar_tipoHistoriaUsuario, name='borrarTipoHistoriaUsuario'),
    path('<int:proyecto_id>/tipo-historia-usuario/importar/', importar_tipoUS, name='importarTipoHistoriaUsuario'),


    path('<int:proyecto_id>/backlog/', historiaUsuarioBacklog, name='historiaUsuarioBacklog'),
    path('<int:proyecto_id>/historias-canceladas/', historiaUsuarioCancelado, name='historiaUsuarioCancelado'),
    path('<int:proyecto_id>/historias-terminadas/', historiaUsuarioTerminado, name='historiaUsuarioTerminado'),
    path('<int:proyecto_id>/mis-historias/', historiaUsuarioAsignado, name='historiaUsuarioAsignado'),

    path('<int:proyecto_id>/historia-usuario/crear/', crear_historiaUsuario, name='crearhistoriaUsuario'),
    path('<int:proyecto_id>/historia-usuario/<int:historia_id>/borrar/', borrar_historiaUsuario, name='borrar_historiaUsuario'),
    path('<int:proyecto_id>/historia-usuario/<int:historia_id>/editar/', editar_historiaUsuario, name='editar_historiaUsuario'),
    path('<int:proyecto_id>/historia-usuario/<int:historia_id>/comentarios/', comentarios_historiaUsuario, name='comentarios_historiaUsuario'),

    path('<int:id_proyecto>/historias/<int:id_historia>/', moverEtapa, name='mover_historias_usuario'),
    path('<int:proyecto_id>/historial/<int:historia_id>/', restaurar_historia_historial, name='restaurar_historia_historial'),
    path('<int:proyecto_id>/tablero/<int:tipo_id>/', verTablero, name='verTablero'),
    path('<int:proyecto_id>/archivos/<int:historia_id>/', ver_archivos, name='ver_archivos'),
]
