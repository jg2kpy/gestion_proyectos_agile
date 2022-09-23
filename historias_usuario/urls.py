from django.urls import path
from .views import tiposHistoriaUsuario, crear_tipoHistoriaUsuario, editar_tipoHistoriaUsuario, borrar_tipoHistoriaUsuario, importar_tipoUS, historiaUsuarioBacklog, historiaUsuarioCancelado, historiaUsuarioTerminado, historiaUsuarioAsignado, crear_historiaUsuario, borrar_historiaUsuario, editar_historiaUsuario, comentarios_historiaUsuario, configHistoriasPendientes, restaurar_historia_historial

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

    path('<int:id_proyecto>/historias/<int:id_historia>/', configHistoriasPendientes, name='config_historias_usuario'),
    path('historial/<int:proyecto_id>/<int:historia_id>/', restaurar_historia_historial, name='restaurar_historia_historial'),
]
