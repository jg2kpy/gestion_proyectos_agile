"""gestion_proyectos_agile URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
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
from proyectos import views as proyectos_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('proyectos/',proyectos_views.proyectos, name='proyectos'),
    path('proyectos/crear/',proyectos_views.crear_proyecto, name='crear_proyecto'),
    #path('proyectos/ver/<int:id_proyecto>/',proyectos_views.ver_proyecto, name='ver_proyecto'),
    #path('proyectos/editar/<int:id_proyecto>/',proyectos_views.editar_proyecto, name='editar_proyecto'),
    path('proyectos/cancelar/<int:id_proyecto>/',proyectos_views.cancelar_proyecto, name='cancelar_proyecto'),
    path('', Home.as_view(), name='home'),
]
