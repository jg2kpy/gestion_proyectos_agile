import datetime
from genericpath import isdir
import glob
from os import makedirs
import os
import django
from django.forms import inlineformset_factory
from django.http import FileResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.db import IntegrityError
from django.views.decorators.cache import never_cache
import pytz
from gestion_proyectos_agile.views import crearNotificacion

from historias_usuario.models import EtapaHistoriaUsuario, HistoriaUsuario, SprintInfo, TipoHistoriaUsusario
import numpy as np

from historias_usuario.models import EtapaHistoriaUsuario, HistoriaUsuario, Tarea, TipoHistoriaUsusario

from .models import *
from .forms import ProyectoConfigurarForm, ProyectoFeriadosForm, ProyectoForm, ProyectoCancelForm, RolProyectoForm
from usuarios.models import Usuario, RolProyecto, PermisoProyecto
from gestion_proyectos_agile.templatetags.gpa_tags import tiene_permiso_en_proyecto, tiene_permiso_en_sistema, tiene_rol_en_proyecto, tiene_rol_en_sistema

import matplotlib.pyplot as plt
from matplotlib.legend_handler import HandlerLine2D

from pathlib import Path
from django.core.files import File

"""
    Enumerador de estados de Proyecto
    Indica los estados de proyecto que puede tener un proyecto
    y los estados que puede tener un proyecto en un momento dado.
"""
# Estados de Proyecto
ESTADOS_PROYECTO = (
    ('Planificacion', 'Planificacion'),
    ('Ejecucion', 'Ejecucion'),
    ('Finalizado', 'Finalizado'),
    ('Cancelado', 'Cancelado'),
    ('En espera', 'En espera'),
)


@never_cache
def proyectos(request):
    """Vista para renderizar la lista de proyectos
    Se renderiza la lista de proyectos que hay en el sistema
    y se muestra el boton para crear un nuevo proyecto

    :param request: Peticion HTTP
    :type request: HttpRequest

    :return: Renderiza la lista de proyectos
    :rtype: HttpResponse
    """

    request_user = request.user

    if not request.user.is_authenticated:
        return render(request, '401.html', status=401)
    
    request.session['cancelar_volver_a'] = request.path

    if tiene_permiso_en_sistema(request_user, 'sys_crearproyectos'):
        return render(request, 'proyectos/base.html', {'proyectos': Proyecto.objects.all()})

    return render(request, 'proyectos/base.html', {'proyectos': Proyecto.objects.filter(usuario=request_user)})


@never_cache
def proyecto_home(request, proyecto_id):
    """Vista de inicio de proyecto

    :param request: Peticion HTTP
    :type request: HttpRequest
    :return: Renderiza la vista de inicio de proyecto
    :rtype: HttpResponse
    """

    if not request.user.is_authenticated:
        return render(request, '401.html', status=401)

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    if not request.user.equipo.filter(id=proyecto.id).exists():
        return render(request, '403.html', {'info_adicional': 'No tiene permisos para ver este proyecto'}, status=403)

    request.session['cancelar_volver_a'] = request.path
    return render(request, 'proyectos/home.html', {'proyecto': proyecto})


@never_cache
def crear_proyecto(request):
    """Funcion para crear un nuevo proyecto
    Renderiza la pagina para crear un nuevo proyecto, recibe una llamada POST con los datos de un proyecto
    y guarda el proyecto, tambien asigna al scrum Master que sera el scrum master del proyecto.

    :param request: Peticion HTTP
    :type request: HttpRequest
    """

    request_user = request.user

    if not request_user.is_authenticated:
        return render(request, '401.html', status=401)

    # Verificar que solo el administrador puede crear proyectos
    if not tiene_permiso_en_sistema(request_user, 'sys_crearproyectos'):
        return render(request, '403.html', {'info_adicional': 'No tiene permisos para crear proyectos'}, status=403)

    formset_factory = inlineformset_factory(
        Proyecto, Feriado, form=ProyectoFeriadosForm, extra=0, can_delete=False)

    if request.method == 'POST':
        form = ProyectoForm(request.POST)
        formset = formset_factory(request.POST, instance=form.instance)

        if form.is_valid():
            # Creamos el proyecto
            proyecto = Proyecto()
            proyecto.nombre = form.cleaned_data['nombre']
            proyecto.descripcion = form.cleaned_data['descripcion']
            # Automaticamente el estado se queda en planificado
            proyecto.estado = ESTADOS_PROYECTO.__getitem__(0)[0]
            scrum_master = form.cleaned_data['scrumMaster']
            proyecto.scrumMaster = scrum_master
            if form.cleaned_data['minimo_dias_sprint']:
                proyecto.minimo_dias_sprint = form.cleaned_data['minimo_dias_sprint']
            if form.cleaned_data['maximo_dias_sprint']:
                proyecto.maximo_dias_sprint = form.cleaned_data['maximo_dias_sprint']
            
            try:
                proyecto.save()

                scrum_master.equipo.add(proyecto)

                for f in formset:
                    feriado = f.save(commit=False)
                    feriado.proyecto = proyecto
                    feriado.save()

            except Exception as e:
                return HttpResponse('Error al crear el proyecto', status=500)

            # Traemos el ID del proyecto recien creado
            # Traemos todos los roles que tenga null como proyecto_id
            roles = RolProyecto.objects.filter(proyecto__isnull=True)
            # Generamos una copia de este rol y el asignamos el id del proyecto
            for rol in roles:
                # Creamos el rol
                rol_nuevo = RolProyecto()
                rol_nuevo.nombre = rol.nombre
                rol_nuevo.descripcion = rol.descripcion
                rol_nuevo.proyecto = Proyecto.objects.get(id=proyecto.id)
                rol_nuevo.save()

                # Traemos los permisos del rol
                permisos = PermisoProyecto.objects.filter(rol=rol)

                # Recorremos los permisos y los asignamos al rol
                for permiso in permisos:
                    # Agregamos el rol al permiso
                    permiso.rol.add(rol_nuevo)
                    permiso.save()

            scrum_master.roles_proyecto.add(RolProyecto.objects.get(
                nombre="Scrum Master", proyecto=proyecto))
            scrum_master.save()

            tipos = TipoHistoriaUsusario.objects.filter(proyecto__isnull=True)

            for tipo in tipos:
                tipo_nuevo = TipoHistoriaUsusario()
                tipo_nuevo.nombre = tipo.nombre
                tipo_nuevo.descripcion = tipo.descripcion
                tipo_nuevo.proyecto = proyecto
                tipo_nuevo.save()

                etapas = EtapaHistoriaUsuario.objects.filter(TipoHistoriaUsusario=tipo)
                for etapa in etapas:
                    etapa_nuevo = EtapaHistoriaUsuario()
                    etapa_nuevo.nombre = etapa.nombre
                    etapa_nuevo.descripcion = etapa.descripcion
                    etapa_nuevo.orden = etapa.orden
                    etapa_nuevo.TipoHistoriaUsusario_id = tipo_nuevo.id
                    etapa_nuevo.save()
                
                tipo_nuevo.save()


            return redirect('proyectos')
        else:
            return HttpResponse('Formulario invalido', status=422)
    else:
        form = ProyectoForm()
        form_feriado = formset_factory()
    return render(request, 'proyectos/crear_proyecto.html', {'form': form, 'form_feriado': form_feriado})


# Editar un proyecto
@never_cache
def editar_proyecto(request, proyecto_id):
    """Funcion para editar un proyecto
    Renderiza la pagina para editar un proyecto, recibe una llamada POST con los datos de un proyecto
    y guarda el proyecto.

    :param request: Peticion HTTP donde se recibe la informacion del proyecto a editar
    :type request: HttpRequest

    :param proyecto_id: ID del proyecto a editar
    :type proyecto_id: int

    :return: Renderiza la pagina para editar un proyecto
    :rtype: HttpResponse
    """

    request_user = request.user

    if not request_user.is_authenticated:
        return render(request, '401.html', status=401)

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    # Verificar que solo con el permiso de cambiar estado de proyecto
    if not tiene_permiso_en_proyecto(request_user, 'pro_cambiarEstadoProyecto', proyecto):
        return render(request, '403.html', {'info_adicional': 'No tiene permisos para editar proyectos'}, status=403)

    formset_factory = inlineformset_factory(
        Proyecto, Feriado, form=ProyectoFeriadosForm, extra=0, can_delete=False)

    # Verificamos que el usuario tenga permisos rol de moderador o es el scrum master del proyecto
    if request.method == 'POST':
        form = ProyectoConfigurarForm(request.POST, instance=proyecto)
        formset = formset_factory(request.POST, instance=form.instance)
        if form.is_valid() and formset.is_valid():
            try:
                # Editamos el proyecto
                proyecto = Proyecto.objects.get(id=proyecto_id)
                proyecto.descripcion = form.cleaned_data['descripcion']
                proyecto.minimo_dias_sprint = form.cleaned_data['minimo_dias_sprint']
                proyecto.maximo_dias_sprint = form.cleaned_data['maximo_dias_sprint']

                proyecto.feriados.all().delete()
                
                proyecto.save()

                for f in formset:
                    feriado = f.save(commit=False)
                    feriado.proyecto = proyecto
                    feriado.save()

                proyecto.save()
                return redirect('proyecto_home', proyecto_id=proyecto.id)
            except Exception as e:
                return HttpResponse('Error al editar el proyecto', status=500)
        else:
            return HttpResponse('Formulario invalido', status=422)
    else:
        proyecto = Proyecto.objects.get(id=proyecto_id)
        form = ProyectoConfigurarForm(instance=proyecto)
        # cargamos los datos del proyecto

        form_feriado = formset_factory(instance=proyecto)

    volver_a = request.session['cancelar_volver_a']
    return render(request, 'proyectos/editar_proyecto.html', {'form': form, 'form_feriado':form_feriado, 'proyecto': proyecto, 'volver_a': volver_a})


# Recibimos una peticion POST para cancelar un proyecto
@never_cache
def cancelar_proyecto(request, proyecto_id):
    """Cancelar Proyecto
    Cambia el estado del proyecto a cancelado, se recibe el nombre del proyecto a cancelar, se verifica que el proyecto coincida con
    el nombre introducido y se cambia el estado a cancelado.

    :param request: Peticion HTTP
    :type request: HttpRequest

    :param proyecto_id: ID del proyecto a cancelar
    :type proyecto_id: int

    :return: Renderiza la pagina de proyectos
    :rtype: HttpResponse
    """

    request_user = request.user

    if not request_user.is_authenticated:
        return render(request, '401.html', status=401)

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    # Verificar que solo con el permiso de cambiar estado de proyecto
    if not tiene_permiso_en_proyecto(request_user, 'pro_cambiarEstadoProyecto', proyecto):
        return render(request, '403.html', {'info_adicional': 'No tiene permisos para cancelar este proyecto'}, status=403)

    if request.method == 'POST':
        form = ProyectoCancelForm(request.POST)
        if form.is_valid():
            # Cancelamos el proyecto
            # verificamos que el nombre del proyecto sea correcto
            if form.cleaned_data['nombre'] == proyecto.nombre:
                proyecto.estado = 'Cancelado'
                
                sprintsCancelar = Sprint.objects.filter(proyecto=proyecto).exclude(estado="Terminado").exclude(estado="Cancelado")
                
                for sprint in sprintsCancelar:
                    sprint.estado = "Cancelado"
                    sprint.save()

                historiasActivas = HistoriaUsuario.objects.filter(proyecto=proyecto, estado='A')
                
                for historia in historiasActivas:
                    historia.estado = HistoriaUsuario.Estado.CANCELADO
                    historia.save()

                proyecto.save()

                usuariosProyecto = Usuario.objects.filter(equipo__id=proyecto.id)
            
                for usuario in usuariosProyecto:
                    crearNotificacion(
                        usuario,
                        f"El proyecto {proyecto.nombre} pasa a estado Cancelado"
                    )

                return redirect('proyectos')
            else:
                return render(request, 'proyectos/base.html', {'proyectos': Proyecto.objects.all()}, status=422)
        else:
            return HttpResponse('Formulario invalido', status=422)
    else:
        form = ProyectoCancelForm()

    # Si el proyecto ya esta cancelado no se puede cancelar de nuevo
    if Proyecto.objects.get(id=proyecto_id).estado == ESTADOS_PROYECTO.__getitem__(3)[0]:
        return redirect('proyectos')

    return render(request, 'proyectos/cancelar_proyecto.html', {'form': form})


@never_cache
def terminar_proyecto(request, proyecto_id):
    """Terminar Proyecto
    Cambia el estado del proyecto a finalizado, se recibe el nombre del proyecto a cancelar, se verifica que el proyecto coincida con
    el nombre introducido y se cambia el estado a finalizado.

    :param request: Peticion HTTP
    :type request: HttpRequest

    :param proyecto_id: ID del proyecto a cancelar
    :type proyecto_id: int

    :return: Renderiza la pagina de proyectos
    :rtype: HttpResponse
    """

    request_user = request.user

    if not request_user.is_authenticated:
        return render(request, '401.html', status=401)

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    # Verificar que solo con el permiso de cambiar estado de proyecto
    if not tiene_permiso_en_proyecto(request_user, 'pro_cambiarEstadoProyecto', proyecto):
        return render(request, '403.html', {'info_adicional': 'No tiene permisos para cancelar este proyecto'}, status=403)

    if request.method == 'POST':
        form = ProyectoCancelForm(request.POST)
        if form.is_valid():
            # Cancelamos el proyecto
            # verificamos que el nombre del proyecto sea correcto
            if form.cleaned_data['nombre'] == proyecto.nombre:
                proyecto.estado = 'Finalizado'
                
                historiasPlanificacion = HistoriaUsuario.objects.filter(proyecto=proyecto, etapa__isnull=True)
                
                for historia in historiasPlanificacion:
                    historia.estado = HistoriaUsuario.Estado.CANCELADO
                    historia.save()

                proyecto.save()

                usuariosProyecto = Usuario.objects.filter(equipo__id=proyecto.id)
            
                for usuario in usuariosProyecto:
                    crearNotificacion(
                        usuario,
                        f"El proyecto {proyecto.nombre} pasa a estado Finalizado"
                    )
                
                return redirect('proyectos')
            else:
                return render(request, 'proyectos/base.html', {'proyectos': Proyecto.objects.all()}, status=422)
        else:
            return HttpResponse('Formulario invalido', status=422)
    else:
        form = ProyectoCancelForm()

    # Si el proyecto ya esta finalizado no se puede finalizar de nuevo
    if Proyecto.objects.get(id=proyecto_id).estado == ESTADOS_PROYECTO.__getitem__(2)[0]:
        return redirect('proyectos')

    return render(request, 'proyectos/terminar_proyecto.html', {'form': form})


# Creamos un rol en un proyecto
@never_cache
def crear_rol_proyecto(request):
    """Crear Rol de Proyecto
    Renderiza la pagina para crear un rol de proyecto, recibe una llamada POST con los datos del rol de proyecto,
    trae los permisos de la base de datos y los muestra en la pagina y guarda el rol de proyecto con sus permisos correspondientes.

    :param request: Peticion HTTP donde se recibe la informacion del rol de proyecto a crear
    :type request: HttpRequest

    :return: Renderiza la pagina para crear un rol de proyecto
    :rtype: HttpResponse
    """

    request_user = request.user

    if not request_user.is_authenticated:
        return render(request, '401.html', status=401)

    # Verificar que solo el administrador puede crear roles de proyectos
    if not tiene_permiso_en_sistema(request_user, 'sys_crearproyectos'):
        return render(request, '403.html', {'info_adicional': 'No tiene permisos para crear roles de proyectos'}, status=403)
        

    if request.method == 'POST':
        form = RolProyectoForm(request.POST)
        if form.is_valid():
            # Creamos el rol
            try:
                rol = RolProyecto()
                rol.nombre = form.cleaned_data['nombre']
                rol.descripcion = form.cleaned_data['descripcion']
                rol.save()

                # Traemos todos los permisos de la base de datos
                permisos = PermisoProyecto.objects.all()

                # Traemos los permisos que se seleccionaron en el formulario
                permisos_seleccionados = form.cleaned_data['permisos']

                # Recorremos los permisos y los asignamos al rol
                for permiso in permisos:
                    if permiso.nombre in permisos_seleccionados.values_list('nombre', flat=True):
                        # Agregamos el rol al permiso
                        permiso.rol.add(rol)
                        permiso.save()

            except Exception as e:
                return HttpResponse('Error al crear el rol de proyecto', status=500)

            return render(request, 'proyectos/roles_proyecto/roles_proyecto.html', {'roles_proyecto': RolProyecto.objects.all()}, status=200)
        else:
            return HttpResponse('Formulario invalido', status=500)
    else:
        form = RolProyectoForm()
    return render(request, 'proyectos/roles_proyecto/crear_rol_proyecto.html', {'form': form}, status=200)


# Ver la informacion de un rol de un proyecto en especifico
@never_cache
def ver_rol_proyecto(request, proyecto_id, id_rol_proyecto):
    """Ver rol de proyecto
    Renderiza la pagina para ver un rol de proyecto, recibe el id del rol de proyecto y muestra la informacion del rol de proyecto
    trae los permisos asociados con el rol indicado

    :param request: Peticion HTTP
    :type request: HttpRequest

    :param id_rol_proyecto: ID del rol de proyecto a ver
    :type id_rol_proyecto: int

    :return: Renderiza la pagina para ver un rol de proyecto
    :rtype: HttpResponse
    """

    request_user = request.user
    try:
        rol = RolProyecto.objects.get(id=id_rol_proyecto)
    except RolProyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este rol."}, status=404)
    proyecto = rol.proyecto

    if not request_user.is_authenticated:
        return render(request, '401.html', status=401)

    if not request.user.equipo.filter(id=proyecto.id).exists():
        return render(request, '403.html', {'info_adicional': 'No tiene permisos para ver roles de proyectos'}, status=403)

    # Traemos los permisos del rol
    permisos = PermisoProyecto.objects.filter(rol=rol)

    return render(request, 'proyectos/roles_proyecto/ver_rol_proyecto.html', {'rol': rol, 'permisos': permisos, 'proyecto': proyecto})


# Modificar un rol de un proyecto
@ never_cache
def modificar_rol_proyecto(request, proyecto_id, id_rol_proyecto):
    """Modificar rol de proyecto
    Renderiza la pagina para modificar un rol de proyecto, recibe una llamada POST con los datos del rol de proyecto,
    trae los permisos de la base de datos los modifica y guarda el rol de proyecto.

    :param request: Peticion HTTP donde se recibe la informacion del rol de proyecto a modificar
    :type request: HttpRequest

    :param id_rol_proyecto: ID del rol de proyecto a modificar
    :type id_rol_proyecto: int

    :return: Renderiza la pagina para modificar un rol de proyecto
    :rtype: HttpResponse
    """

    request_user = request.user

    if not request_user.is_authenticated:
        return render(request, '401.html', status=401)

    # Verificar que solo el administrador y el Scrum Master pueden modificar roles de proyectos

    try:
        rol = RolProyecto.objects.get(id=id_rol_proyecto)
    except RolProyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este rol."}, status=404)

    proyecto = rol.proyecto

    if not tiene_permiso_en_proyecto(request_user, 'pro_editarRolProyecto', proyecto):
        return render(request, '403.html', {'info_adicional': 'No tiene permisos para modificar roles de proyectos'}, status=403)

    # Traemos los permisos del rol
    permisos = PermisoProyecto.objects.filter(rol=rol)

    if request.method == 'POST':
        form = RolProyectoForm(request.POST)
        if form.is_valid():
            # Modificamos el rol
            rol.nombre = form.cleaned_data['nombre']
            rol.descripcion = form.cleaned_data['descripcion']
            rol.save()

            # Traemos todos los permisos de la base de datos
            permisos = PermisoProyecto.objects.all()

            # Traemos los permisos que se seleccionaron en el formulario
            permisos_seleccionados = form.cleaned_data['permisos']

            # Recorremos los permisos y los asignamos al rol
            for permiso in permisos:
                if permiso.nombre in permisos_seleccionados.values_list('nombre', flat=True):
                    # Agregamos el rol al permiso
                    permiso.rol.add(rol)
                    permiso.save()
                else:
                    # Eliminamos el rol del permiso
                    permiso.rol.remove(rol)
                    permiso.save()
        if (rol.proyecto is None):
            return render(request, 'proyectos/roles_proyecto/roles_proyecto.html', {'roles_proyecto': RolProyecto.objects.all(), 'usuario': request.user})
        else:
            return redirect('roles_de_proyecto', proyecto_id=proyecto.id)
    else:
        form = RolProyectoForm(
            initial={'nombre': rol.nombre, 'descripcion': rol.descripcion, 'permisos': rol.permisos.all() })
    return render(request, 'proyectos/roles_proyecto/modificar_rol_proyecto.html', {'form': form, 'rol': rol, 'permisos': permisos, 'proyecto': proyecto})


# Eliminar un rol de un proyecto
@ never_cache
def eliminar_rol_proyecto(request, proyecto_id, id_rol_proyecto):
    """Eliminar rol de proyecto
    Elimina un rol de proyecto, recibe el id del rol de proyecto a eliminar y lo elimina de la base de datos

    :param request: Peticion HTTP
    :type request: HttpRequest

    :param id_rol_proyecto: ID del rol de proyecto a eliminar
    :type id_rol_proyecto: int

    :return: Renderiza la pagina para ver los roles de proyecto
    """

    request_user = request.user

    if not request_user.is_authenticated:
        return render(request, '401.html', status=401)

    # Verificar que solo el administrador y el Scrum Master pueden modificar roles de proyectos

    try:
        rol = RolProyecto.objects.get(id=id_rol_proyecto)
    except RolProyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este rol."}, status=404)

    proyecto = rol.proyecto

    if not tiene_permiso_en_proyecto(request_user, 'pro_editarRolProyecto', proyecto):
        return render(request, '403.html', {'info_adicional': 'No tiene permisos para eliminar roles de proyectos'}, status=403)

    if request.method == 'POST':
        rol = RolProyecto.objects.get(id=id_rol_proyecto)
        rol.delete()
        if (rol.proyecto is None):
            return render(request, 'proyectos/roles_proyecto/roles_proyecto.html', {'roles_proyecto': RolProyecto.objects.all(), 'usuario': request.user})
        else:
            return redirect('roles_de_proyecto', proyecto_id=proyecto.id)
    return redirect('roles_de_proyecto', proyecto_id=proyecto.id)


# Ver roles asignados a un proyecto
@ never_cache
def roles_de_proyecto(request, proyecto_id):
    """Ver roles de un proyecto especifico
    Renderiza la pagina para ver los roles de proyecto asignados a un proyecto, recibe el id del proyecto

    :param request: Peticion HTTP
    :type request: HttpRequest

    :param id_usuario: ID del usuario a ver los roles de proyecto asignados
    :type id_usuario: int

    :return: Renderiza la pagina para ver los roles de proyecto asignados a un usuario
    :rtype: HttpResponse
    """

    request_user = request.user
    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    # Verificacion que o es SrumMaster o es admin del sistema
    if not request_user.is_authenticated:
        return render(request, '401.html', status=401)

    # Verificar que solo el administrador puede crear roles de proyectos
    if not tiene_permiso_en_proyecto(request.user, 'pro_cambiarEstadoProyecto', proyecto) and not tiene_permiso_en_sistema(request.user, 'sys_crearproyectos'):
        return render(request, '403.html', {'info_adicional': 'No tiene permisos para ver los roles de este proyecto'}, status=403)

    # Traemos los roles que tengan el id del proyecto
    try:
        roles = RolProyecto.objects.filter(proyecto=proyecto_id)
    except RolProyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    return render(request, 'proyectos/roles_proyecto/roles_proyecto.html', {'roles_proyecto': roles, 'proyecto': proyecto})


# Creamos un rol en un proyecto a un proyecto especifico
@ never_cache
def crear_rol_a_proyecto(request, proyecto_id):
    """Crear y asignar rol de proyecto a un proyecto especifico
    Renderiza la pagina para crear un rol de proyecto y asignarlo a un proyecto especifico, recibe una llamada POST con los datos del rol de proyecto,
    trae los permisos de la base de datos y los muestra en la pagina y guarda el rol de proyecto.

    :param request: Peticion HTTP donde se recibe la informacion del rol de proyecto a crear
    :type request: HttpRequest

    :param proyecto_id: ID del proyecto al que se le asignara el rol de proyecto
    :type proyecto_id: int

    :return: Renderiza la pagina para crear un rol de proyecto y asignarlo a un proyecto especifico
    :rtype: HttpResponse
    """

    request_user = request.user
    # Verificar si esta autenticado
    if not request_user.is_authenticated:
        return render(request, '401.html', status=401)

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    if not tiene_permiso_en_proyecto(request_user, 'pro_crearRolProyecto', proyecto):
        return render(request, '403.html', {'info_adicional': 'No tiene permisos para crear roles de proyectos'}, status=403)

    status = 200

    if request.method == 'POST':
        form = RolProyectoForm(request.POST)
        if form.is_valid():
            # Creamos el rol
            rol = RolProyecto()
            rol.nombre = form.cleaned_data['nombre']
            rol.descripcion = form.cleaned_data['descripcion']
            rol.proyecto = Proyecto.objects.get(id=proyecto_id)
            try:
                rol.save()
            except IntegrityError:
                form.add_error('nombre', 'Ya existe un rol con ese nombre')
                status = 422
                return render(request, 'proyectos/roles_proyecto/crear_rol_proyecto.html', {'form': form, 'proyecto': proyecto}, status=status)

            # Traemos todos los permisos de la base de datos
            permisos = PermisoProyecto.objects.all()

            # Traemos los permisos que se seleccionaron en el formulario
            permisos_seleccionados = form.cleaned_data['permisos']

            # Recorremos los permisos y los asignamos al rol
            for permiso in permisos:
                if permiso.nombre in permisos_seleccionados.values_list('nombre', flat=True):
                    # Agregamos el rol al permiso
                    permiso.rol.add(rol)
                    permiso.save()

            return redirect('roles_de_proyecto', proyecto_id=proyecto.id)
        else:
            status = 422

    else:
        form = RolProyectoForm()
    return render(request, 'proyectos/roles_proyecto/crear_rol_proyecto.html', {'form': form, 'proyecto': proyecto}, status=status)


# Importar Rol de otros proyectos
@ never_cache
def importar_rol(request, proyecto_id):
    """Importar rol de proyecto
    Renderiza la pagina para importar un rol de proyecto.
    Recibe una llamada GET para renderizar la pantalla pero con los roles del proyecto a importar.
    Recibe una llamada POST para importar el rol de proyecto seleccionado.

    :param request: Peticion HTTP donde se recibe la informacion del rol de proyecto a importar
    :type request: HttpRequest

    :param proyecto_id: ID del proyecto al que se le importara el rol de proyecto
    :type proyecto_id: int

    :return: Renderiza la pagina para importar un rol de proyecto
    :rtype: HttpResponse
    """

    request_user = request.user

    # Verificamos que el usuario este autenticado
    if not request_user.is_authenticated:
        return render(request, '401.html', status=401)

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    # Verificacion que o es SrumMaster o es admin del sistema
    if not tiene_permiso_en_proyecto(request_user, 'pro_importarRol', proyecto):
        return render(request, '403.html', {'info_adicional': 'No tiene permisos para importar roles de proyecto'}, status=403)

    if request.method == 'POST':
        # proyecto_id: Proyecto a donde se VA A IMPORTAR
        roles = []  # Lista de los id de los roles a importar
        proyecto_seleccionado = Proyecto.objects.get(id=int(request.POST.get(
            'proyecto_seleccionado')))  # Proyecto de donde SE IMPORTA los roles
        for rol in proyecto_seleccionado.roles.all():
            if request.POST.get(f'{rol.id}') != None:
                roles.append(rol)

        # Recorremos los roles y creamos nuevos roles con los mismos permisos
        for rol in roles:
            if rol.nombre not in RolProyecto.objects.filter(proyecto=proyecto_id).values_list('nombre', flat=True):
                # Creamos el rol
                rol_nuevo = RolProyecto()
                rol_nuevo.nombre = rol.nombre
                rol_nuevo.descripcion = rol.descripcion
                rol_nuevo.proyecto = Proyecto.objects.get(id=proyecto_id)
                rol_nuevo.save()

                # Traemos los permisos del rol
                permisos = PermisoProyecto.objects.filter(rol=rol)

                # Recorremos los permisos y los asignamos al rol
                for permiso in permisos:
                    # Agregamos el rol al permiso
                    permiso.rol.add(rol_nuevo)
                    permiso.save()

        return redirect('roles_de_proyecto', proyecto_id=proyecto.id)

    else:
        proyectos = Proyecto.objects.exclude(id=proyecto_id)
        # proyecto_objetivo = Proyecto.objects.get(nombre = request.GET.get('proyectos'))
        # Este es el GET cuando solicita ver los roles de proyectos de un proyecto en especifico
        if request.GET.get('proyectos'):
            proyecto_seleccionado = Proyecto.objects.get(
                nombre=request.GET.get('proyectos'))
            roles = RolProyecto.objects.filter(proyecto=proyecto_seleccionado)
        else:  # Este es el GET cuando se llama desde otra pagina
            roles = None
            if proyectos.count() == 0:
                proyecto_seleccionado = None
            else:
                proyecto_seleccionado = proyectos[0]
                roles = RolProyecto.objects.filter(proyecto=proyectos[0])
        
        if roles:
            rolesPropios = RolProyecto.objects.filter(proyecto=proyecto_id).values_list('nombre', flat=True)
            roles = roles.exclude(nombre__in=rolesPropios)


    return render(request, 'proyectos/roles_proyecto/importar_rol.html', {'proyectos': proyectos, 'proyecto_seleccionado': proyecto_seleccionado, 'roles': roles, 'proyecto': proyecto})

@never_cache
def crear_sprint(request, proyecto_id):
    """Crear sprint
    Renderiza la pagina para crear un sprint.
    Recibe una llamada POST para crear el sprint.

    :param request: Peticion HTTP donde se recibe la informacion del sprint a crear
    :type request: HttpRequest

    :param proyecto_id: ID del proyecto al que se le creara el sprint
    :type proyecto_id: int

    :return: Renderiza la pagina para crear un sprint
    :rtype: HttpResponse
    """

    request_user = request.user

    if not request_user.is_authenticated:
        return render(request, '401.html', status=401)

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    if not tiene_permiso_en_proyecto(request_user, 'pro_especificarTiempoDeSprint', proyecto):
        return render(request, '403.html', {'info_adicional': 'No tiene permisos para crear sprints'}, status=403)

    historias = [x for x in sorted(proyecto.backlog.all(), key=lambda x: x.getPrioridad(), reverse=True) if x.getPrioridad() >= 0]
    status = 200
    error = None
    sprint = Sprint()
    if request.method == 'POST':
        sprint.proyecto = proyecto
        sprint.estado = "Planificado"
        sprint.duracion = request.POST.get('duracion')
        sprint.nombre = request.POST.get('nombre')
        sprint.descripcion = request.POST.get('descripcion')

        sprint.save()
        for historia in historias:
            if request.POST.get('historia_seleccionado_'+str(historia.id)):
                historia.sprint = sprint
                historia.horasAsignadas = request.POST.get('historia_horas_'+str(historia.id))
                historia.usuarioAsignado = Usuario.objects.get(id=request.POST.get('desarrollador_asignado_'+str(historia.id)))
                historia.save()
            
            if historia.usuarioAsignado:
                crearNotificacion(
                    historia.usuarioAsignado,
                    f"Se le ha asignado la historia de usuario {historia.nombre} perteneciente al sprint {historia.sprint.nombre} dentro del proyecto {historia.proyecto.nombre}"
                )
        
        for usuario in proyecto.usuario.all():
            horas = request.POST.get('horas_trabajadas_'+str(usuario.id))
            if horas and int(horas) >= 0:
                tiempoSprint = UsuarioTiempoEnSprint()
                tiempoSprint.sprint = sprint
                tiempoSprint.usuario = usuario
                tiempoSprint.horas = horas
                tiempoSprint.save()
                

        return redirect('backlog_sprint', sprint.proyecto.id, sprint.id)


    else:
        pass

    return render(request, 'sprints/crear.html', {'proyecto': proyecto, 'desarrolladores': list(proyecto.usuario.all().values_list('id', flat=True)), 'historias': historias, 'error': error, 'sprint': sprint}, status=status)

def calcularFechaSprint(fechaInicio, dias, proyecto):
    """
        Realiza el cálculo de la fecha final del sprint.

        :param fechaInicio: Fecha inicial del sprint
        :type fechaInicio: datetime

        :param dias: Total de duración del sprint en días
        :type dias: int

        :param proyecto: Proyecto en el que se encuentra el sprint
        :type proyecto: int

        :return: Retorna la fecha de final del sprint
        :rtype: datetime
    """
    diasParaAgregar = dias
    fechaActual = fechaInicio
    feriadosFecha = []
    feriados = Feriado.objects.filter(proyecto=proyecto)

    if feriados:
        for feriado in feriados:
            feriadosFecha.append(feriado.fecha.date())
    
    while diasParaAgregar > 0:
        
        if not (fechaActual.weekday() >= 5 or fechaActual.date() in feriadosFecha):
            diasParaAgregar -= 1

        if diasParaAgregar > 0:
            fechaActual += datetime.timedelta(days=1)

    
    return fechaActual

@never_cache
def backlog_sprint(request, proyecto_id, sprint_id):
    """Crear sprint
    Renderiza la pagina para crear un sprint.
    Recibe una llamada POST para iniciar o cancelar el sprint.

    :param request: Peticion HTTP donde se recibe la informacion del sprint a crear
    :type request: HttpRequest

    :param sprint_id: ID del sprint que se quiere visualizar
    :type sprint_id: int

    :return: Renderiza la pagina para manejar el backlog de un sprint
    :rtype: HttpResponse
    """

    request_user = request.user

    if not request_user.is_authenticated:
        return render(request, '401.html', status=401)

    try:
        sprint = Sprint.objects.get(id=sprint_id)
        proyecto = sprint.proyecto
    except Sprint.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este sprint."}, status=404)

    if not tiene_permiso_en_proyecto(request_user, 'pro_especificarTiempoDeSprint', proyecto):
        return render(request, '403.html', {'info_adicional': 'No tiene permisos para crear sprints'}, status=403)
    if sprint.estado == "Terminado":
        return render(request, '403.html', {'info_adicional': 'No puede ver backlogs de Sprint terminado'}, status=403)

    if request.method == 'POST':
        if request.POST.get('historia_id'):
            historia = HistoriaUsuario.objects.get(id=request.POST.get('historia_id'))
            historia.sprint = None
            historia.save()
        elif request.POST.get('cancelar'):
            if sprint.fecha_inicio != None:
                return render(request, '403.html', {'info_adicional': 'Sprint ya iniciado'}, status=422)
            if Sprint.objects.filter(estado="Desarrollo",proyecto=proyecto).count() > 0:
                return render(request, '403.html', {'info_adicional': 'Ya existe un sprint activo'}, status=422)

            sprint.estado = "Cancelado"
            sprint.fecha_inicio = datetime.datetime.now(tz=django.utils.timezone.get_current_timezone()).replace(hour=0, minute=0, second=0, microsecond=0)
            sprint.save()

            usListFinalizar = HistoriaUsuario.objects.filter(proyecto=proyecto, sprint=sprint,estado=HistoriaUsuario.Estado.ACTIVO)
            for usFinalizar in usListFinalizar:
                usFinalizar.sprint = None
                usFinalizar.horasAsignadas = 0
                usFinalizar.usuarioAsignado = None
                usFinalizar.save()
            
            proyecto.estado = "Planificación"
            proyecto.save()

            return redirect('sprint_list', proyecto_id=proyecto.id)
        else:
            if sprint.fecha_inicio != None:
                return render(request, '403.html', {'info_adicional': 'Sprint ya iniciado'}, status=422)
            if Sprint.objects.filter(estado="Desarrollo",proyecto=proyecto).count() > 0:
                return render(request, '403.html', {'info_adicional': 'Ya existe un sprint activo'}, status=422)
            sprint.fecha_inicio = datetime.datetime.now(tz=django.utils.timezone.get_current_timezone()).replace(hour=0, minute=0, second=0, microsecond=0)
            sprint.fecha_fin = calcularFechaSprint(sprint.fecha_inicio, sprint.duracion, proyecto).replace(hour=0, minute=0, second=0, microsecond=0)
            sprint.estado = "Desarrollo"
            sprint.save()

            #Mover a la primera etapa en caso de que el US esta en planificacion
            historias_en_planificacion = sprint.historias.filter(etapa=None)
            for historia in historias_en_planificacion:
                sigEtapa = EtapaHistoriaUsuario.objects.get(
                            orden=0, TipoHistoriaUsusario=historia.tipo)
                historia.etapa = sigEtapa
                historia.save()

            proyecto.estado = "Ejecución"
            proyecto.save()
        
    miembros = [miembro for miembro in proyecto.usuario.all() if UsuarioTiempoEnSprint.objects.filter(sprint=sprint, usuario=miembro).exists()]
    capacidad_total = 0
    capacidad_asignada = 0
    for miembro in miembros:
        miembro.historias_total = sum([historia.horasAsignadas for historia in sprint.historias.filter(estado='A') if historia.usuarioAsignado == miembro])
        capacidad_asignada += miembro.historias_total
        miembro.capacidad = UsuarioTiempoEnSprint.objects.get(sprint=sprint, usuario=miembro).horas
        miembro.capacidad_total = miembro.capacidad * sprint.duracion
        capacidad_total += miembro.capacidad_total
        miembro.historias_count = len([historia for historia in sprint.historias.filter(estado='A') if historia.usuarioAsignado == miembro])
    

    request.session['cancelar_volver_a'] = request.path

    return render(request, 'sprints/base.html', {'proyecto': proyecto, 'capacidad_asignada': capacidad_asignada, 'capacidad_total':capacidad_total, 'miembros': miembros, 'sprint': sprint, 'historias': sprint.historias.filter(estado=HistoriaUsuario.Estado.ACTIVO), 'titulo': "Sprint Backlog "+sprint.nombre}, status=200)

@never_cache
def editar_miembros_sprint(request, proyecto_id, sprint_id):
    """
    Permite editar la lista de miembros con las que trabajan de un Sprint

    :param request: Peticion HTTP
    :type request: HttpRequest

    :param proyecto_id: ID del proyecto al que pertenece el sprint
    :type proyecto_id: int

    :param sprint_id: ID del sprint del cuál se quiere modificar el equipo
    :type sprint_id: int

    :return: Renderiza la pagina para editar los miembros del sprint
    :rtype: HttpResponse
    """

    request_user = request.user

    if not request_user.is_authenticated:
        return render(request, '401.html', status=401)

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
        sprint = Sprint.objects.get(id=sprint_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto o sprint."}, status=404)

    if not tiene_permiso_en_proyecto(request_user, 'pro_especificarTiempoDeSprint', proyecto):
        return render(request, '403.html', {'info_adicional': 'No tiene permisos para crear sprints'}, status=403)
    if sprint.estado != "Planificado":
        return render(request, '403.html', {'info_adicional': f'No puede editar miembros de un Sprint que no se encuentra en planificación. Este Sprint esta en estado {sprint.estado}'}, status=403)

    desarrolladores = proyecto.usuario.all()
    status = 200
    error = None
    if request.method == 'POST':
        for usuario in desarrolladores:
            horas = request.POST.get('horas_trabajadas_'+str(usuario.id))
            if horas and int(horas) > 0:
                if UsuarioTiempoEnSprint.objects.filter(usuario=usuario, sprint=sprint).exists():
                    tiempoSprint = UsuarioTiempoEnSprint.objects.get(usuario=usuario, sprint=sprint)
                else:
                    tiempoSprint = UsuarioTiempoEnSprint(usuario=usuario, sprint=sprint)
                tiempoSprint.horas = horas
                tiempoSprint.save()
                return redirect('backlog_sprint', sprint.proyecto.id, sprint.id)
            else:
                status = 422
    else:
        for d in desarrolladores:
            try:
                d.horas = UsuarioTiempoEnSprint.objects.get(usuario=d, sprint=sprint).horas
                d.horas_total = 0
                for historia in sprint.historias.filter(usuarioAsignado=d):
                    d.horas_total += historia.horasAsignadas
            except UsuarioTiempoEnSprint.DoesNotExist:
                d.horas = 0

    return render(request, 'sprints/editar_miembros.html', {'proyecto': proyecto, 'desarrolladores': desarrolladores, 'error': error, 'sprint': sprint}, status=status)

@never_cache
def agregar_historias_sprint(request, proyecto_id, sprint_id):
    """
    Permite agregar US a un Sprint

    :param request: Peticion HTTP
    :type request: HttpRequest

    :param proyecto_id: ID del proyecto al que pertenece el sprint
    :type proyecto_id: int

    :param sprint_id: ID del sprint del cuál se quiere modificar el equipo
    :type sprint_id: int

    :return: Renderiza la pagina para editar los miembros del sprint
    :rtype: HttpResponse
    """

    request_user = request.user

    if not request_user.is_authenticated:
        return render(request, '401.html', status=401)

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
        sprint = Sprint.objects.get(id=sprint_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto o sprint."}, status=404)

    if not tiene_permiso_en_proyecto(request_user, 'pro_especificarTiempoDeSprint', proyecto):
        return render(request, '403.html', {'info_adicional': 'No tiene permisos para crear sprints'}, status=403)
    
    if sprint.estado != "Planificado":
        return render(request, '403.html', {'info_adicional': 'No puede agregar historias a un Sprint que no se encuentra en planificación.'}, status=403)

    historias = [x for x in sorted(proyecto.backlog.all(), key=lambda x: x.getPrioridad(), reverse=True) if x.getPrioridad() >= 0]
    status = 200
    error = None
    if request.method == 'POST':
        for historia in historias:
            if request.POST.get('historia_seleccionado_'+str(historia.id)):
                historia.sprint = sprint
                historia.horasAsignadas = request.POST.get('historia_horas_'+str(historia.id))
                historia.usuarioAsignado =  Usuario.objects.get(id=request.POST.get('desarrollador_asignado_'+str(historia.id)))
                historia.save()

                if historia.usuarioAsignado:
                    crearNotificacion(
                        historia.usuarioAsignado,
                        f"Se le ha asignado la historia {historia.nombre} perteneciente al sprint {historia.sprint} dentro del proyecto {proyecto.nombre} dentro del proyecto {historia.proyecto.nombre}"
                    )

        return redirect('backlog_sprint', sprint.proyecto.id, sprint.id)

    return render(request, 'sprints/agregar_historias.html', {'proyecto': proyecto, 'historias': historias, 'error': error, 'sprint': sprint}, status=status)

@never_cache
def reasignar_us(request, proyecto_id, historia_id):
    """
    Permite reasignar una historia de usuario

    :param request: Peticion HTTP
    :type request: HttpRequest

    :param proyecto_id: ID del proyecto al que pertenece el sprint
    :type proyecto_id: int

    :param historia_id: ID de la historia de usuario a reasignar
    :type historia_id: int

    :return: Renderiza la pagina para reasignar
    :rtype: HttpResponse
    """

    request_user = request.user

    if not request_user.is_authenticated:
        return render(request, '401.html', status=401)

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
        historia = HistoriaUsuario.objects.get(id=historia_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto o sprint."}, status=404)

    if not tiene_permiso_en_proyecto(request_user, 'pro_crearTipoUS', proyecto):
        return render(request, '403.html', {'info_adicional': 'No tiene permisos para reasignar'}, status=403)

    status = 200
    error = None
    if request.method == 'POST':

        if historia.usuarioAsignado:
            crearNotificacion(
                historia.usuarioAsignado,
                f"Usted ha sido desasignado de la historia de usuario {historia.nombre} perteneciente al proyecto {historia.proyecto.nombre}"
            )

        historia.usuarioAsignado =  Usuario.objects.get(id=request.POST.get('desarrollador_asignado_'+str(historia.id)))
        historia.save()

        crearNotificacion(
            historia.usuarioAsignado,
            f"Usted ha sido asignado a la historia de usuario {historia.nombre} perteneciente al proyecto {historia.proyecto.nombre}"
        )

        return redirect('backlog_sprint', proyecto.id, historia.sprint.id)

    return render(request, 'sprints/reasignar_historia.html', {'proyecto': proyecto, 'historia': historia, 'error': error}, status=status)


def calcularHorasDiarias(sprint, cantDiasSprint, fechaInicial, feriados):
    """
    Permite calcular las horas diarias que tiene realizado un sprint

    :param sprint: Sprint a querer analizar
    :type sprint: Sprint

    :param cantDiasSprint: Cantidad de días que posee el sprint
    :type cantDiasSprint: int

    :param fechaInicial: Fecha inicial del sprint
    :type fechaInicial: datetime

    :return: Retorna un array con las horas realizadas por día
    :rtype: list[int]
    """
    fechaActual = fechaInicial
    totalHorasDiario = []
    feriadosFecha = []
    
    if feriados:
        for feriado in feriados:
            feriadosFecha.append(feriado.fecha.date())

    while cantDiasSprint:
        if not (fechaActual.weekday() >= 5 or feriados and fechaActual.date() in feriadosFecha):
            cantDiasSprint -= 1
            tareasDiarias = Tarea.objects.filter(sprint=sprint, fecha=fechaActual)
            sumaHoras = 0
            
            for tarea in tareasDiarias:
                sumaHoras += tarea.horas

            totalHorasDiario.append(sumaHoras)

        if cantDiasSprint > 0:
            fechaActual += datetime.timedelta(days=1)

    return totalHorasDiario


def calcularHorasSprint(sprint):
    """
    Permite calcular las horas totales que posee el sprint

    :param sprint: Sprint a querer analizar
    :type sprint: Sprint

    :return: Retorna el total que horas que posee un sprint
    :rtype: int
    """
    usList = HistoriaUsuario.objects.filter(sprint=sprint, estado__in=["S","T"])
    totalHoras = 0

    for us in usList:
        totalHoras += us.horasAsignadas
    
    return totalHoras


def generarGraficoBurndown(x, yTeorico, yReal):
    """
    Genera el gráfico Burndown

    :param x: Lista de valores enteros para el eje x
    :type x: list[int]

    :param yTeorico: Lista de valores enteros para el eje y del valor teórico
    :type yTeorico: list[int]

    :param yReal: Lista de valores enteros para el eje y del valor real
    :type yReal: list[int]
    """

    fig, ax = plt.subplots()
    ax.set_xlabel("Días")
    ax.set_ylabel("Horas")
    line1, = ax.plot(x, yTeorico, label="Tareas Ideales", linestyle='-', marker='o', color='b')
    line2, = ax.plot(x, yReal, label="Tareas Reales", linestyle='-', marker='o', color='r')
    ax.legend(handler_map={line1: HandlerLine2D()})
    plt.title("Burndown Chart")
    

def generarBurndownChart(sprintId):
    """
    Calcula los datos necesarios para el gráfico Burndown y genera el gráfico

    :param sprintId: Id del sprint a querer crear el gráfico
    :type sprintId: int
    """

    # if ArchivoBurndown.objects.filter(sprint__id=sprintId).exists():
    #     return

    # Datos para realizar los cálculos
    sprint = Sprint.objects.get(id=sprintId)
    cantDiasSprint = sprint.duracionOri if sprint.duracion < sprint.duracionOri else sprint.duracion
    inicioSprint = sprint.fecha_inicio
    feriados = Feriado.objects.filter(proyecto=sprint.proyecto)
    horasUsDiario = calcularHorasDiarias(sprint, cantDiasSprint, inicioSprint, feriados)
    horasTotalSprint = calcularHorasSprint(sprint)

    # Inicio de los cálculos
    x = [dias for dias in range(cantDiasSprint + 1)]
    yTeorico = [horasTotalSprint]
    yReal = [horasTotalSprint]

    # Para el horario ideal
    horasRestanteSprint = horasTotalSprint
    horasIdealDiario = int(horasTotalSprint / cantDiasSprint)

    for _ in range(cantDiasSprint):
        horasRestanteSprint -= horasIdealDiario
        yTeorico.append(horasRestanteSprint)

    # Para el horario real
    horasRestanteSprint = horasTotalSprint

    for horasUs in horasUsDiario:
        horasRestanteSprint = horasRestanteSprint - horasUs
        yReal.append(horasRestanteSprint)

    generarGraficoBurndown(x, yTeorico, yReal)
    if not isdir('/django/app/staticfiles/temp'):
        makedirs("/django/app/staticfiles/temp")
    plt.savefig(f"/django/app/staticfiles/temp/bdChart_{sprint.proyecto.id}_{sprint.id}.png")
    plt.close()

    rutaImg = Path(f"/django/app/staticfiles/temp/bdChart_{sprint.proyecto.id}_{sprint.id}.png")
    
    if ArchivoBurndown.objects.filter(sprint__id=sprintId).exists():
        archivoBurndown = ArchivoBurndown.objects.get(sprint__id=sprintId)
    else:
        archivoBurndown = ArchivoBurndown()
    
    archivoBurndown.nombre = f"bdChart_{sprint.proyecto.id}_{sprint.id}"
    
    with rutaImg.open(mode='rb') as archivo:
        archivoBurndown.archivo = File(archivo, name=f"app/staticfiles/bdChart_{sprint.proyecto.id}_{sprint.id}.png")
        archivoBurndown.save()
        sprint.burndownChart = archivoBurndown
        sprint.save()


def generarVelocityChart(proyectoId):
    """
    Calcula los datos necesarios para el gráfico Velocity y genera el gráfico

    :param proyectoId: Id del proyecto a querer crear el gráfico
    :type proyectoId: int
    """

    velChart = None
    if ArchivoVelocity.objects.filter(proyecto__id=proyectoId).exists():
        velChart = ArchivoVelocity.objects.get(proyecto__id=proyectoId)
    else:
        velChart = ArchivoVelocity()
        velChart.nombre = f"velocityChart_{proyectoId}"

    # Datos para realizar los cálculos
    proyecto = Proyecto.objects.get(id=proyectoId)
    sprints = Sprint.objects.filter(proyecto__id=proyectoId, estado="Terminado")
    horasTotalSprintList = []
    horasUsSprintList = []
    sprintNombreList = []

    for sprint in sprints:
        cantDiasSprint = sprint.duracion
        inicioSprint = sprint.fecha_inicio
        feriados = Feriado.objects.filter(proyecto=sprint.proyecto)
        sprintNombreList.append(sprint.nombre)
        horasUsDiario = calcularHorasDiarias(sprint, cantDiasSprint, inicioSprint, feriados)
        horasTotalSprintList.append(calcularHorasSprint(sprint))
        
        tempUsTotal = 0

        for horaUs in horasUsDiario:
            tempUsTotal += horaUs
        
        horasUsSprintList.append(tempUsTotal)
    
    generarGraficoVelocity(horasTotalSprintList, horasUsSprintList, sprintNombreList)
    plt.savefig(f"/django/app/staticfiles/temp/vlChart_{proyecto.id}.png")
    plt.close()
    rutaImg = Path(f"/django/app/staticfiles/temp/vlChart_{proyecto.id}.png")
    
    with rutaImg.open(mode='rb') as archivo:
        velChart.archivo = File(archivo, name=f"app/staticfiles/vlChart_{proyecto.id}.png")
        velChart.proyecto = proyecto
        velChart.save()


def generarGraficoVelocity(horasTotalSprintList, horasUsSprintList, sprintNombreList):
    """
    Genera el gráfico Velocity

    :param horasTotalSprintList: Lista de valores enteros con el total de horas a completar por sprint
    :type horasTotalSprintList: list[int]

    :param horasUsSprintList: Lista de valores enteros con el total de horas completados por sprint
    :type horasUsSprintList: list[int]

    :param sprintNombreList: Lista de valores con los nombres de los sprints
    :type sprintNombreList: list[int]
    """

    cantBarras = len(horasTotalSprintList)
    barraIzq = horasTotalSprintList
    barrDer = horasUsSprintList
    ind = np.arange(cantBarras)
    ancho = 0.3

    plt.figure(figsize=(10,5))

    plt.bar(ind, barraIzq , ancho, label='Trabajo propuesto')
    plt.bar(ind + ancho, barrDer, ancho, label='Trabajo realizado')

    plt.ylabel('Horas')
    plt.title('Velocity Chart')
    plt.xticks(ind + ancho / 2, sprintNombreList)

    plt.legend(loc='best')
    plt.show()


@never_cache
def descargarReporte(request, id):
    """
    Permite descargar un archivo.

    :param request: HttpRequest
    :type request: HttpRequest
    :param id: Id del sprint o del proyecto al que pertenece el reporte
    :type id: int
    :rtype: HttpResponse
    """
    
    if 'descargarBurndown' in request.POST:
        try:
            archivo = ArchivoBurndown.objects.get(sprint__id=id)
        except ArchivoBurndown.DoesNotExist:
            return render(request, '404.html', {'info_adicional': "No se encontró este archivo."}, status=404)
    else:
        try:
            archivo = ArchivoVelocity.objects.get(proyecto__id=id)
        except ArchivoVelocity.DoesNotExist:
            return render(request, '404.html', {'info_adicional': "No se encontró este archivo."}, status=404)

    return FileResponse(open(archivo.archivo.path, 'rb'), content_type='application/force-download')


@never_cache
def sprint_list(request, proyecto_id):
    """
    Permite ver una lista de Sprints

    :param request: Peticion HTTP
    :type request: HttpRequest

    :param proyecto_id: ID del proyecto al que pertenecen los sprint
    :type proyecto_id: int

    :return: Renderiza la pagina para ver los sprints
    :rtype: HttpResponse
    """

    request_user = request.user

    if not request_user.is_authenticated:
        return render(request, '401.html', status=401)

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto o sprint."}, status=404)

    if not tiene_rol_en_proyecto(request.user, "Scrum Master", proyecto):
        return render(request, '403.html', {'info_adicional': 'No tiene permisos para crear sprints'}, status=403)

    hayCambio = False

    sprints = Sprint.objects.filter(proyecto=proyecto)

    for sprint in sprints:
        if sprint.estado == "Terminado" and not os.path.isfile(f"app/staticfiles/bdChart_{proyecto.id}_{sprint.id}.png"):
            hayCambio = True
            generarBurndownChart(sprint.id) 

    if hayCambio:
        generarVelocityChart(proyecto.id)

    files = glob.glob('app/staticfiles/temp/*')
    for f in files:
        os.remove(f)

    if request.method == 'POST':
        if 'descargarBurndown' in request.POST:
            sprintId = request.POST['descargarBurndown']
            return descargarReporte(request, sprintId)
        else:
            proyectoId = request.POST['descargarVelocity']
            return descargarReporte(request, proyecto_id)

            
    return render(request, 'sprints/sprintList.html', {'proyecto': proyecto}, status=200)

@never_cache
def sprint_reemplazar_miembro(request, proyecto_id, sprint_id):
    """
    Permite reemplazar un miembro de un sprint

    :param request: Peticion HTTP
    :type request: HttpRequest

    :param sprint_id: ID del sprint al que pertenece el miembro
    :type sprint_id: int

    :return: Renderiza la pagina para ver el formulario de reemplazo de miembro
    :rtype: HttpResponse
    """

    request_user = request.user

    if not request_user.is_authenticated:
        return render(request, '401.html', status=401)

    try:
        sprint = Sprint.objects.get(id=sprint_id)
    except Sprint.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto o sprint."}, status=404)

    if not tiene_rol_en_proyecto(request.user, "Scrum Master", sprint.proyecto):
        return render(request, '403.html', {'info_adicional': 'No tiene permisos para reemplazar un miembro'}, status=403)

    error = None
    if request.method == 'POST':
        usuario_sale = request.POST.get('usuario_sale')
        usuario_entra = request.POST.get('usuario_entra')

        (res, error) = sprint.reemplazar_miembro(Usuario.objects.get(id=usuario_sale), Usuario.objects.get(id=usuario_entra))
        if res:
            return redirect('backlog_sprint', proyecto_id=sprint.proyecto.id, sprint_id=sprint.id)
    
    activos = [Usuario.objects.get(id=usuario) for usuario in sprint.participantes.all().values_list('usuario', flat=True)]
    suplentes = [usuario for usuario in sprint.proyecto.usuario.all() if usuario not in activos]

    return render(request, 'sprints/reemplazar_miembro.html', {'proyecto': sprint.proyecto, 'sprint': sprint, 'activos': activos, 'suplentes': suplentes, 'error': error}, status=200)
