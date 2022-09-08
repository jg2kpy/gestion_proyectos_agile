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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', Home.as_view(), name='home'),

    path('rolesglobales/', usuarios_views.rol_global_list, name='rol_global_list'),
    path('rolesglobales/crear/', usuarios_views.rol_global_crear, name='rol_global_crear'),
    path('rolesglobales/<int:id>/editar/', usuarios_views.rol_global_editar, name='rol_global_editar'),
    path('rolesglobales/<int:id>/usuarios/', usuarios_views.rol_global_usuarios, name='rol_global_usuarios'),
    path('usuarios/', include('usuarios.urls'), name='usuarios'),
    path('perfil/', usuarios_views.perfil, name='perfil')
]
