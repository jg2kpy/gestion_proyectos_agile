"""gestion_proyectos_agile URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/

Examples:

Function views
    1. Add an import: from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')

Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from .views import Home
from usuarios import views as usuarios_views
from proyectos import views as proyectos_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('tipo-historia-usuario/', include('historias_usuario.urls')),
    path('<int:id_proyecto>/', proyectos_views.proyecto_home, name='proyecto_home'),
    path('proyectos/', proyectos_views.proyectos, name='proyectos'),
    path('proyectos/crear/', proyectos_views.crear_proyecto, name='crear_proyecto'),
    path('proyectos/<int:id_proyecto>/editar/', proyectos_views.editar_proyecto, name='editar_proyecto'),
    path('proyectos/cancelar/<int:id_proyecto>/', proyectos_views.cancelar_proyecto, name='cancelar_proyecto'),
    path('proyectos/roles_proyecto/', proyectos_views.roles_proyecto, name='roles_proyecto'),
    path('proyectos/roles_proyecto/crear/', proyectos_views.crear_rol_proyecto, name='crear_rol_proyecto'),
    path('proyectos/roles_proyecto/<int:id_rol_proyecto>/', proyectos_views.ver_rol_proyecto, name='ver_rol_proyecto'),
    path('proyectos/roles_proyecto/editar/<int:id_rol_proyecto>/', proyectos_views.modificar_rol_proyecto, name='modificar_rol_proyecto'),
    path('proyectos/roles_proyecto/eliminar/<int:id_rol_proyecto>/', proyectos_views.eliminar_rol_proyecto, name='eliminar_rol_proyecto'),
    path('proyectos/<int:id_proyecto>/roles/', proyectos_views.ver_roles_asignados, name='rol_proyecto_asignado'),
    path('proyectos/<int:id_proyecto>/roles/crear/', proyectos_views.crear_rol_a_proyecto, name='crear_rol_a_proyecto'),
    path('proyectos/<int:id_proyecto>/roles/import/', proyectos_views.importar_rol, name='importar_rol'),
    path('', Home.as_view(), name='home'),

    path('rolesglobales/', usuarios_views.rol_global_list, name='rol_global_list'),
    path('rolesglobales/crear/', usuarios_views.rol_global_crear, name='rol_global_crear'),
    path('rolesglobales/<int:id>/editar/', usuarios_views.rol_global_editar, name='rol_global_editar'),
    path('rolesglobales/<int:id>/usuarios/', usuarios_views.rol_global_usuarios, name='rol_global_usuarios'),
    path('usuarios/', include('usuarios.urls'), name='usuarios'),
    path('perfil/', usuarios_views.perfil, name='perfil')
]
