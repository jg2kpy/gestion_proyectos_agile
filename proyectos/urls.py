from django.urls import path

from proyectos.views import *

urlpatterns = [
    path('', proyectos, name='proyectos'),
    path('crear/', crear_proyecto, name='crear_proyecto'),

    path('<int:id_proyecto>/', proyecto_home, name='proyecto_home'),
    path('<int:id_proyecto>/editar/', editar_proyecto, name='editar_proyecto'),
    path('<int:id_proyecto>/cancelar/', cancelar_proyecto, name='cancelar_proyecto'),

    path('<int:id_proyecto>/roles/', ver_roles_asignados, name='rol_proyecto_asignado'),
    path('<int:id_proyecto>/roles/crear/', crear_rol_a_proyecto, name='crear_rol_a_proyecto'),
    path('<int:id_proyecto>/roles_proyecto/<int:id_rol_proyecto>/', ver_rol_proyecto, name='ver_rol_proyecto'),
    path('<int:id_proyecto>/roles_proyecto/<int:id_rol_proyecto>/editar/', modificar_rol_proyecto, name='modificar_rol_proyecto'),
    path('<int:id_proyecto>/roles_proyecto/<int:id_rol_proyecto>/eliminar/', eliminar_rol_proyecto, name='eliminar_rol_proyecto'),
    
    path('<int:id_proyecto>/roles/import/', importar_rol, name='importar_rol'),
]
