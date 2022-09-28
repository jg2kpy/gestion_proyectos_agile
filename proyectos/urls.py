from django.urls import path

from proyectos.views import *

urlpatterns = [
    path('', proyectos, name='proyectos'),
    path('crear/', crear_proyecto, name='crear_proyecto'),

    path('<int:proyecto_id>/', proyecto_home, name='proyecto_home'),
    path('<int:proyecto_id>/editar/', editar_proyecto, name='editar_proyecto'),
    path('<int:proyecto_id>/cancelar/', cancelar_proyecto, name='cancelar_proyecto'),

    path('<int:proyecto_id>/roles/', ver_roles_asignados, name='rol_proyecto_asignado'),
    path('<int:proyecto_id>/roles/crear/', crear_rol_a_proyecto, name='crear_rol_a_proyecto'),
    path('<int:proyecto_id>/roles_proyecto/<int:id_rol_proyecto>/', ver_rol_proyecto, name='ver_rol_proyecto'),
    path('<int:proyecto_id>/roles_proyecto/<int:id_rol_proyecto>/editar/', modificar_rol_proyecto, name='modificar_rol_proyecto'),
    path('<int:proyecto_id>/roles_proyecto/<int:id_rol_proyecto>/eliminar/', eliminar_rol_proyecto, name='eliminar_rol_proyecto'),
    
    path('<int:proyecto_id>/roles/import/', importar_rol, name='importar_rol'),
]
