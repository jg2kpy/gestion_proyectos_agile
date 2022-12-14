from django.urls import path

from proyectos.views import *

urlpatterns = [
    path('', proyectos, name='proyectos'),
    path('crear/', crear_proyecto, name='crear_proyecto'),

    path('<int:proyecto_id>/', proyecto_home, name='proyecto_home'),
    path('<int:proyecto_id>/editar/', editar_proyecto, name='editar_proyecto'),
    path('<int:proyecto_id>/cancelar/', cancelar_proyecto, name='cancelar_proyecto'),
    path('<int:proyecto_id>/terminar/', terminar_proyecto, name='terminar_proyecto'),

    path('<int:proyecto_id>/roles/', roles_de_proyecto, name='roles_de_proyecto'),
    path('<int:proyecto_id>/roles/crear/', crear_rol_a_proyecto, name='crear_rol_a_proyecto'),
    path('<int:proyecto_id>/roles/<int:id_rol_proyecto>/', ver_rol_proyecto, name='ver_rol_proyecto'),
    path('<int:proyecto_id>/roles/<int:id_rol_proyecto>/editar/', modificar_rol_proyecto, name='modificar_rol_proyecto'),
    path('<int:proyecto_id>/roles/<int:id_rol_proyecto>/eliminar/', eliminar_rol_proyecto, name='eliminar_rol_proyecto'),
    
    path('<int:proyecto_id>/roles/import/', importar_rol, name='importar_rol'),

    path('<int:proyecto_id>/sprints/crear/', crear_sprint, name='crear_sprint'),
    path('<int:proyecto_id>/sprints/<int:sprint_id>/backlog/', backlog_sprint, name='backlog_sprint'),
    path('<int:proyecto_id>/sprints/<int:sprint_id>/editar_miembros/', editar_miembros_sprint, name='editar_miembros_sprint'),
    path('<int:proyecto_id>/sprints/<int:sprint_id>/agregar_historias/', agregar_historias_sprint, name='agregar_historias_sprint'),
    path('<int:proyecto_id>/sprints/reasignar_us/<int:historia_id>/', reasignar_us, name='reasignar_us'),
    path('<int:proyecto_id>/sprints/list/', sprint_list, name='sprint_list'),
    path('<int:proyecto_id>/sprints/<int:sprint_id>/reemplazar_miembro/', sprint_reemplazar_miembro, name='sprint_reemplazar_miembro'),
]
