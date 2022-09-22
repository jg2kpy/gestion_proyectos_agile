from django.urls import path
from .views import borrar_historiaUsuario, comentarios_historiaUsuario, crear_historiaUsuario, crear_tipoHistoriaUsuario, editar_historiaUsuario, historiaUsuarioAsignado, historiaUsuarioBacklog, historiaUsuarioCancelado, historiaUsuarioTerminado, tiposHistoriaUsuario, editar_tipoHistoriaUsuario, borrar_tipoHistoriaUsuario, importar_tipoUS

urlpatterns = [
    path('tipo-historia-usuario/<int:proyecto_id>/', tiposHistoriaUsuario, name='tiposHistoriaUsuario'),
    path('tipo-historia-usuario/crear/<int:proyecto_id>/', crear_tipoHistoriaUsuario, name='crearTipoHistoriaUsuario'),
    path('tipo-historia-usuario/editar/<int:proyecto_id>/<int:tipo_id>/', editar_tipoHistoriaUsuario, name='editarTipoHistoriaUsuario'),
    path('tipo-historia-usuario/borrar/<int:proyecto_id>/<int:tipo_id>/', borrar_tipoHistoriaUsuario, name='borrarTipoHistoriaUsuario'),
    path('tipo-historia-usuario/importar/<int:proyecto_id>/', importar_tipoUS, name='importarTipoHistoriaUsuario'),

    path('backlog/<int:proyecto_id>/', historiaUsuarioBacklog, name='historiaUsuarioBacklog'),
    path('historias-canceladas/<int:proyecto_id>/', historiaUsuarioCancelado, name='historiaUsuarioCancelado'),
    path('historias-terminadas/<int:proyecto_id>/', historiaUsuarioTerminado, name='historiaUsuarioTerminado'),
    path('mis-historias/<int:proyecto_id>/', historiaUsuarioAsignado, name='historiaUsuarioAsignado'),
    path('historia-usuario/crear/<int:proyecto_id>/', crear_historiaUsuario, name='crearhistoriaUsuario'),
    path('historia-usuario/borrar/<int:proyecto_id>/<int:historia_id>/', borrar_historiaUsuario, name='borrar_historiaUsuario'),
    path('historia-usuario/editar/<int:proyecto_id>/<int:historia_id>/', editar_historiaUsuario, name='editar_historiaUsuario'),
    path('historia-usuario/comentarios/<int:proyecto_id>/<int:historia_id>/', comentarios_historiaUsuario, name='comentarios_historiaUsuario'),
]
