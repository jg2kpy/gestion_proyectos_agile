from http.client import HTTPResponse
from django.shortcuts import render, redirect

from gestion_proyectos_agile.templatetags.tiene_rol_en import tiene_rol_en_proyecto
from proyectos.models import Proyecto
from usuarios.models import RolProyecto, Usuario

# Create your views here.

def eliminar_mienbro_proyecto(request, proyecto_nombre, usuario_nombre):
    if not request.user.is_authenticated:
        return HTTPResponse(status=401)
    
    usuario_a_desvincular = Usuario.objects.filter(username = usuario_nombre).first()
    proyecto = Proyecto.objects.filter(nombre = proyecto_nombre).first()
    rol = RolProyecto.objects.filter(usuario = usuario_a_desvincular, proyecto = proyecto)
    usuario_a_desvincular.equipo.remove(proyecto)
    usuario_a_desvincular.roles_proyecto.get(nombre = rol.nombre).remove()

    return redirect('home')