from django.http import HttpResponse
from django.shortcuts import render, redirect

from gestion_proyectos_agile.templatetags.tiene_rol_en import tiene_rol_en_proyecto
from proyectos.models import Proyecto
from usuarios.models import RolProyecto, Usuario

# Create your views here.

"""
Las vistas relacionadas al package de usuarios
"""


def eliminar_miembro_proyecto(request):
    """Eliminar miembros de un proyecto

    :param request: Solicitud HTTP del cliente junto con el body con los datos del nombre de usuario id del proyecto
    :type request: HttpRequest

    :return: Se retorna una respuesta HttpResponse que puede ser un 401 en caso de no tener la autorizacion o retornar a la pagina principal
    :rtype: HttpResponse
    """

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return HttpResponse('Usuario no autenticado', status=401)

        form = request.POST

        usuario_nombre = form.get('usuario_a_eliminar')
        proyecto_id = form.get('proyecto')

        if not tiene_rol_en_proyecto(request.user, "Scrum Master", proyecto_id):
            return HttpResponse('Usuario no pertenece al proyecto o no posee el permiso de realizar esta accion', status=401)

        try:
            usuario_a_eliminar_miembro_proyecto = Usuario.objects.get(username=usuario_nombre)
            proyecto = Proyecto.objects.get(id=proyecto_id)
            roles = RolProyecto.objects.filter(usuario=usuario_a_eliminar_miembro_proyecto, proyecto=proyecto_id)
            [usuario_a_eliminar_miembro_proyecto.roles_proyecto.remove(r) for r in roles]
            usuario_a_eliminar_miembro_proyecto.equipo.remove(proyecto)
        except Usuario.DoesNotExist:
            return HttpResponse('Usuario no existe', status=404)

    return redirect('home')


def agregar_miembro_proyecto(request):
    """Agregar miembro al proyecto

    :param request: Solicitud HTTP del cliente junto con el body con los datos del nombre de usuario id del proyecto e ir del rol
    :type request: HttpRequest

    :return: Se retorna una respuesta HttpResponse que puede ser un 401 en caso de no tener la autorizacion o retornar a la pagina principal
    :rtype: HttpResponse
    """
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return HttpResponse('Usuario no autenticado', status=401)

        form = request.POST
        usuario_nombre = form.get('usuario_a_agregar')
        proyecto_id = form.get('proyecto')
        rol_id = form.get('roles_agregar')

        if not tiene_rol_en_proyecto(request.user, "Scrum Master", proyecto_id):
            return HttpResponse('Usuario no pertenece al proyecto o no posee el permiso de realizar esta accion', status=401)

        try:
            usuario_a_agregar_miembro_proyecto = Usuario.objects.get(
                username=usuario_nombre)
            proyecto = Proyecto.objects.get(id=proyecto_id)

            if usuario_a_agregar_miembro_proyecto.equipo.filter(id=proyecto.id).count() != 0:
                return render(request, 'base.html', {'mensaje': 'El usuario ya pertenece al proyecto'})

            usuario_a_agregar_miembro_proyecto.equipo.add(proyecto)
            rol_proyecto = RolProyecto.objects.get(id=rol_id)
            usuario_a_agregar_miembro_proyecto.roles_proyecto.add(rol_proyecto)
        except Usuario.DoesNotExist:
            return HttpResponse('Usuario no existe', status=404)

    return redirect('home')


def eliminar_rol_proyecto(request):
    """Eliminar miembros de un proyecto

    :param request: Solicitud HTTP del cliente junto con el body con los datos del nombre de usuario, id del proyecto e id del rol
    :type request: HttpRequest

    :return: Se retorna una respuesta HttpResponse que puede ser un 401 en caso de no tener la autorizacion o retornar a la pagina principal
    :rtype: HttpResponse
    """

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return HttpResponse('Usuario no autenticado', status=401)

        form = request.POST

        usuario_nombre = form.get('usuario_a_sacar_rol')
        proyecto_id = form.get('proyecto')
        rol_id = form.get('rol_id')

        if not tiene_rol_en_proyecto(request.user, "Scrum Master", proyecto_id):
            return HttpResponse('Usuario no pertenece al proyecto o no posee el permiso de realizar esta accion', status=401)

        try:
            usuario_a_eliminar_rol = Usuario.objects.get(username=usuario_nombre)
            rol = RolProyecto.objects.get(id=rol_id)
            usuario_a_eliminar_rol.roles_proyecto.remove(rol)
        except Usuario.DoesNotExist:
            return HttpResponse('Usuario no existe', status=404)

    return redirect('home')


def asignar_rol_proyecto(request):
    """Asignar un rol de proyecto a un usuario

    :param request: Solicitud HTTP del cliente junto con el body con los datos del nombre de usuario, id del proyecto e id del rol
    :type request: HttpRequest

    :return: Se retorna una respuesta HttpResponse que puede ser un 401 en caso de no tener la autorizacion o retornar a la pagina principal
    :rtype: HttpResponse
    """
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return HttpResponse('Usuario no autenticado', status=401)

        form = request.POST
        usuario_nombre = form.get('usuario_a_cambiar_rol')
        proyecto_id = form.get('proyecto')
        rol_id = form.get(f'roles{usuario_nombre}')

        if not tiene_rol_en_proyecto(request.user, "Scrum Master", proyecto_id):
            return HttpResponse('Usuario no pertenece al proyecto o no posee el permiso de realizar esta accion', status=401)

        try:
            usuario_a_eliminar_rol = Usuario.objects.get(username=usuario_nombre)
            rol = RolProyecto.objects.get(id=rol_id)
            usuario_a_eliminar_rol.roles_proyecto.add(rol)
        except Usuario.DoesNotExist:
            return HttpResponse('Usuario no existe', status=404)

    return redirect('home')
