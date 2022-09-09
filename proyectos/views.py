from warnings import catch_warnings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.db import IntegrityError

import usuarios
from .models import Proyecto
from .forms import ProyectoForm, ProyectoCancelForm, RolProyectoForm
from usuarios.models import Usuario, RolProyecto, PermisoProyecto
from django.views.decorators.cache import never_cache
from gestion_proyectos_agile.templatetags.tiene_rol_en import tiene_permiso_en_proyecto, tiene_permiso_en_sistema, tiene_rol_en_proyecto, tiene_rol_en_sistema
from django.http import HttpResponse

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


"""
    Vista para renderizar la lista de proyectos
    Se renderiza la lista de proyectos que hay en el sistema
    y se muestra el boton para crear un nuevo proyecto

    :param request: Peticion HTTP
    :type request: HttpRequest

    :return: Renderiza la lista de proyectos
    :rtype: HttpResponse
"""


@never_cache
def proyectos(request):

    request_user = request.user

    if not request.user.is_authenticated:
        return HttpResponse('Usuario no autenticado', status=401)

    if not tiene_permiso_en_sistema(request_user, 'sys_crearproyectos'):
        return HttpResponse('No tiene permisos para administrar proyectos', status=403)

    return render(request, 'proyectos/base.html', {'proyectos': Proyecto.objects.all()})


@never_cache
def proyecto_home(request, id_proyecto):
    """
    Vista de inicio de proyecto

    :param request: Peticion HTTP
    :type request: HttpRequest
    :return: Renderiza la vista de inicio de proyecto
    :rtype: HttpResponse
    """
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/", status=401)

    try:
        proyecto = Proyecto.objects.get(id=id_proyecto)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    if not request.user.equipo.filter(id=proyecto.id).exists():
        return HttpResponseRedirect("/", status=422)

    return render(request, 'proyectos/home.html', {'proyecto': proyecto})


"""
    Funcion para crear un nuevo proyecto
    Renderiza la pagina para crear un nuevo proyecto, recibe una llamada POST con los datos de un proyecto
    y guarda el proyecto, tambien asigna al scrum Master que sera el scrum master del proyecto.

    :param request: Peticion HTTP
    :type request: HttpRequest
"""


@never_cache
def crear_proyecto(request):

    request_user = request.user

    if not request_user.is_authenticated:
        return HttpResponse('Usuario no autenticado', status=401)

    # Verificar que solo el administrador puede crear proyectos
    if not tiene_permiso_en_sistema(request_user, 'sys_crearproyectos'):
        return HttpResponse('No tiene permisos para crear proyectos', status=403)

    if request.method == 'POST':
        form = ProyectoForm(request.POST)
        if form.is_valid():
            try:
                # Creamos el proyecto
                proyecto = Proyecto()
                proyecto.nombre = form.cleaned_data['nombre']
                proyecto.descripcion = form.cleaned_data['descripcion']
                proyecto.estado = ESTADOS_PROYECTO.__getitem__(0)[0]  # Automaticamente el estado se queda en planificado
                id_scrum_master = form.cleaned_data['scrum_master']
                scrum_master = Usuario.objects.get(id=id_scrum_master)
                proyecto.scrumMaster = scrum_master
                proyecto.save()

                scrum_master.equipo.add(proyecto)

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

                scrum_master.roles_proyecto.add(RolProyecto.objects.get(nombre="Scrum Master", proyecto=proyecto))
                scrum_master.save()
            except Exception as e:
                return HttpResponse('Error al crear el proyecto', status=500)

            return render(request, 'proyectos/base.html', {'proyectos': Proyecto.objects.all()})
        else:
            return HttpResponse('Formulario invalido', status=422)
    else:
        form = ProyectoForm()
    return render(request, 'proyectos/crear_proyecto.html', {'form': form})


"""
    Funcion para editar un proyecto
    Renderiza la pagina para editar un proyecto, recibe una llamada POST con los datos de un proyecto
    y guarda el proyecto.

    :param request: Peticion HTTP donde se recibe la informacion del proyecto a editar
    :type request: HttpRequest

    :param id_proyecto: ID del proyecto a editar
    :type id_proyecto: int

    :return: Renderiza la pagina para editar un proyecto
    :rtype: HttpResponse
"""
# Editar un proyecto


@never_cache
def editar_proyecto(request, id_proyecto):

    request_user = request.user

    if not request_user.is_authenticated:
        return HttpResponse('Usuario no autenticado', status=401)

    # Verificar que solo el administrador puede editar proyectos
    if not tiene_permiso_en_sistema(request_user, 'sys_crearproyectos'):
        return HttpResponse('No tiene permisos para editar proyectos', status=403)

    try:
        proyecto = Proyecto.objects.get(id=id_proyecto)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    # Verificamos que el usuario tenga permisos rol de moderador o es el scrum master del proyecto
    if request.method == 'POST':
        form = ProyectoForm(request.POST)
        if form.is_valid():
            try:
                # Editamos el proyecto
                proyecto = Proyecto.objects.get(id=id_proyecto)
                proyecto.nombre = form.cleaned_data['nombre']
                proyecto.descripcion = form.cleaned_data['descripcion']
                proyecto.fecha_inicio = form.cleaned_data['fecha_inicio']
                proyecto.fecha_fin = form.cleaned_data['fecha_fin']
                proyecto.save()
                return render(request, 'proyectos/base.html', {'proyectos': Proyecto.objects.all()})
            except Exception as e:
                return HttpResponse('Error al editar el proyecto', status=500)
        else:
            return HttpResponse('Formulario invalido', status=422)
    else:
        form = ProyectoForm()
        # cargamos los datos del proyecto
        proyecto = Proyecto.objects.get(id=id_proyecto)
        form.fields['nombre'].initial = proyecto.nombre
        form.fields['descripcion'].initial = proyecto.descripcion

    return render(request, 'proyectos/editar_proyecto.html', {'form': form})


"""
    Cancelar Proyecto
    Cambia el estado del proyecto a cancelado, se recibe el nombre del proyecto a cancelar, se verifica que el proyecto coincida con
    el nombre introducido y se cambia el estado a cancelado.

    :param request: Peticion HTTP
    :type request: HttpRequest

    :param id_proyecto: ID del proyecto a cancelar
    :type id_proyecto: int

    :return: Renderiza la pagina de proyectos
    :rtype: HttpResponse
"""
# Recibimos una peticion POST para cancelar un proyecto


@never_cache
def cancelar_proyecto(request, id_proyecto):
    request_user = request.user

    if not request_user.is_authenticated:
        return HttpResponse('Usuario no autenticado', status=401)

    # Verificar que solo el administrador puede cancelar proyectos
    if not tiene_permiso_en_sistema(request_user, 'sys_crearproyectos'):
        return HttpResponse('No tiene permisos para cancelar proyectos', status=403)

    try:
        proyecto = Proyecto.objects.get(id=id_proyecto)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    if request.method == 'POST':
        form = ProyectoCancelForm(request.POST)
        if form.is_valid():
            # Cancelamos el proyecto
            # verificamos que el nombre del proyecto sea correcto
            if form.cleaned_data['nombre'] == Proyecto.objects.get(id=id_proyecto).nombre:
                proyecto = Proyecto.objects.get(id=id_proyecto)
                proyecto.estado = 'Cancelado'
                proyecto.save()
                return render(request, 'proyectos/base.html', {'proyectos': Proyecto.objects.all()})
            else:
                return render(request, 'proyectos/base.html', {'proyectos': Proyecto.objects.all()}, status=422)
        else:
            return HttpResponse('Formulario invalido', status=422)
    else:
        form = ProyectoCancelForm()

    # Si el proyecto ya esta cancelado no se puede cancelar de nuevo
    if Proyecto.objects.get(id=id_proyecto).estado == ESTADOS_PROYECTO.__getitem__(3)[0]:
        return render(request, 'proyectos/base.html', {'proyectos': Proyecto.objects.all()})

    return render(request, 'proyectos/cancelar_proyecto.html', {'form': form})

# Creamos una vista para ver los roles de proyectos


@never_cache
def roles_proyecto(request):
    """
        Ver Roles de Proyecto
        Renderiza la pagina para ver los roles de un proyecto, recibe el id del proyecto y muestra los roles de ese proyecto

        :param request: Peticion HTTP
        :type request: HttpRequest
    """
    request_user = request.user

    if not request_user.is_authenticated:
        return HttpResponse('Usuario no autenticado', status=401)

    # Verificar que solo el administrador puede ver los roles de proyectos
    if not tiene_permiso_en_sistema(request_user, 'sys_crearproyectos'):
        return HttpResponse('No tiene permisos para ver los roles de proyectos', status=403)

    return render(request, 'proyectos/roles_proyecto/roles_proyecto.html', {'roles_proyecto': RolProyecto.objects.all()})

# Creamos un rol en un proyecto


@never_cache
def crear_rol_proyecto(request):
    """
        Crear Rol de Proyecto
        Renderiza la pagina para crear un rol de proyecto, recibe una llamada POST con los datos del rol de proyecto,
        trae los permisos de la base de datos y los muestra en la pagina y guarda el rol de proyecto con sus permisos correspondientes.

        :param request: Peticion HTTP donde se recibe la informacion del rol de proyecto a crear
        :type request: HttpRequest

        :return: Renderiza la pagina para crear un rol de proyecto
        :rtype: HttpResponse
    """
    request_user = request.user

    if not request_user.is_authenticated:
        return HttpResponse('Usuario no autenticado', status=401)

    # Verificar que solo el administrador puede crear roles de proyectos
    if not tiene_permiso_en_sistema(request_user, 'sys_crearproyectos'):
        return HttpResponse('No tiene permisos para crear roles de proyectos', status=403)

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
def ver_rol_proyecto(request, id_rol_proyecto):
    """
        Ver rol de proyecto
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
        return HttpResponse('Usuario no autenticado', status=401)

    # Si es proyecto None entonces si o si tiene que ser un gpa_admin
    if proyecto is None and not tiene_rol_en_sistema(request_user, 'gpa_admin'):
        return HttpResponse('No tiene permisos para ver roles de proyectos', status=403)
    elif proyecto is not None and not tiene_rol_en_proyecto(request_user, 'Scrum Master', proyecto):
        return HttpResponse('No tiene permisos para ver roles de proyectos', status=403)

    # Traemos los permisos del rol
    permisos = PermisoProyecto.objects.filter(rol=rol)

    return render(request, 'proyectos/roles_proyecto/ver_rol_proyecto.html', {'rol': rol, 'permisos': permisos, 'proyecto': proyecto})


# Modificar un rol de un proyecto
@ never_cache
def modificar_rol_proyecto(request, id_rol_proyecto):
    """
        Modificar rol de proyecto
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
        return HttpResponse('Usuario no autenticado', status=401)

    # Verificar que solo el administrador y el Scrum Master pueden modificar roles de proyectos

    try:
        rol = RolProyecto.objects.get(id=id_rol_proyecto)
    except RolProyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este rol."}, status=404)

    proyecto = rol.proyecto

    # Si es proyecto None entonces si o si tiene que ser un gpa_admin
    if proyecto is None and not tiene_permiso_en_sistema(request_user, 'sys_crearproyectos'):
        return HttpResponse('No tiene permisos para modificar roles de proyectos', status=403)
    elif proyecto is not None and not tiene_rol_en_proyecto(request_user, 'Scrum Master', proyecto):
        return HttpResponse('No tiene permisos para modificar roles de proyectos', status=403)

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
            return redirect(f'/proyectos/{rol.proyecto.id}/roles/')
    else:
        form = RolProyectoForm(initial={'nombre': rol.nombre, 'descripcion': rol.descripcion})
    return render(request, 'proyectos/roles_proyecto/modificar_rol_proyecto.html', {'form': form, 'rol': rol, 'permisos': permisos, 'proyecto': proyecto})

# Eliminar un rol de un proyecto


@ never_cache
def eliminar_rol_proyecto(request, id_rol_proyecto):
    """
        Eliminar rol de proyecto
        Elimina un rol de proyecto, recibe el id del rol de proyecto a eliminar y lo elimina de la base de datos

        :param request: Peticion HTTP
        :type request: HttpRequest

        :param id_rol_proyecto: ID del rol de proyecto a eliminar
        :type id_rol_proyecto: int

        :return: Renderiza la pagina para ver los roles de proyecto
    """
    request_user = request.user

    if not request_user.is_authenticated:
        return HttpResponse('Usuario no autenticado', status=401)

    # Verificar que solo el administrador y el Scrum Master pueden modificar roles de proyectos

    try:
        rol = RolProyecto.objects.get(id=id_rol_proyecto)
    except RolProyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este rol."}, status=404)

    proyecto = rol.proyecto

    # Si es proyecto None entonces si o si tiene que ser un gpa_admin
    if proyecto is None and not tiene_rol_en_sistema(request_user, 'gpa_admin'):
        return HttpResponse('No tiene permisos para eliminar roles de proyectos', status=403)
    elif proyecto is not None and not tiene_rol_en_proyecto(request_user, 'Scrum Master', proyecto):
        return HttpResponse('No tiene permisos para eliminar roles de proyectos', status=403)

    if request.method == 'POST':
        rol = RolProyecto.objects.get(id=id_rol_proyecto)
        rol.delete()
        if (rol.proyecto is None):
            return render(request, 'proyectos/roles_proyecto/roles_proyecto.html', {'roles_proyecto': RolProyecto.objects.all(), 'usuario': request.user})
        else:
            return redirect(f'/proyectos/{rol.proyecto.id}/roles/')
    return render(request, 'proyectos/roles_proyecto/eliminar_rol_proyecto.html', {'rol_proyecto': RolProyecto.objects.get(id=id_rol_proyecto), 'proyecto': proyecto})


@ never_cache
# Ver roles asignados a un proyecto
def ver_roles_asignados(request, id_proyecto):
    """
        ver roles de un proyecto especifico
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
        proyecto = Proyecto.objects.get(id=id_proyecto)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    # Verificacion que o es SrumMaster o es admin del sistema
    if not request_user.is_authenticated:
        return HttpResponse('Usuario no autenticado', status=401)

    # Verificar que solo el administrador puede crear roles de proyectos
    if not tiene_rol_en_proyecto(request_user, 'Scrum Master', proyecto):
        return HttpResponse('No tiene permisos para ver los roles de este proyecto', status=403)

    # Traemos los roles que tengan el id del proyecto
    try:
        roles = RolProyecto.objects.filter(proyecto=id_proyecto)
    except RolProyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    return render(request, 'proyectos/roles_proyecto/roles_proyecto.html', {'roles_proyecto': roles, 'proyecto': proyecto})

# Creamos un rol en un proyecto a un proyecto especifico


@ never_cache
def crear_rol_a_proyecto(request, id_proyecto):
    """
        Crear y asignar rol de proyecto a un proyecto especifico
        Renderiza la pagina para crear un rol de proyecto y asignarlo a un proyecto especifico, recibe una llamada POST con los datos del rol de proyecto,
        trae los permisos de la base de datos y los muestra en la pagina y guarda el rol de proyecto.

        :param request: Peticion HTTP donde se recibe la informacion del rol de proyecto a crear
        :type request: HttpRequest

        :param id_proyecto: ID del proyecto al que se le asignara el rol de proyecto
        :type id_proyecto: int

        :return: Renderiza la pagina para crear un rol de proyecto y asignarlo a un proyecto especifico
        :rtype: HttpResponse

    """

    request_user = request.user
    # Verificar si esta autenticado
    if not request_user.is_authenticated:
        return HttpResponse('Usuario no autenticado', status=401)

    try:
        proyecto = Proyecto.objects.get(id=id_proyecto)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    # Si es proyecto None entonces si o si tiene que ser un gpa_admin
    if proyecto is None and not tiene_rol_en_sistema(request_user, 'gpa_admin'):
        return HttpResponse('No tiene permisos para crear roles de proyectos', status=403)
    elif proyecto is not None and not tiene_rol_en_proyecto(request_user, 'Scrum Master', proyecto):
        return HttpResponse('No tiene permisos para crear roles de proyectos', status=403)

    status = 200

    if request.method == 'POST':
        form = RolProyectoForm(request.POST)
        if form.is_valid():
            # Creamos el rol
            rol = RolProyecto()
            rol.nombre = form.cleaned_data['nombre']
            rol.descripcion = form.cleaned_data['descripcion']
            rol.proyecto = Proyecto.objects.get(id=id_proyecto)
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

            return redirect(f'/proyectos/{id_proyecto}/roles/')
        else:
            status = 422

    else:
        form = RolProyectoForm()
    return render(request, 'proyectos/roles_proyecto/crear_rol_proyecto.html', {'form': form, 'proyecto': proyecto}, status=status)

# Importar Rol de otros proyectos


@ never_cache
def importar_rol(request, id_proyecto):
    """
        Importar rol de proyecto
        Renderiza la pagina para importar un rol de proyecto.
        Recibe una llamada GET para renderizar la pantalla pero con los roles del proyecto a importar.
        Recibe una llamada POST para importar el rol de proyecto seleccionado.

        :param request: Peticion HTTP donde se recibe la informacion del rol de proyecto a importar
        :type request: HttpRequest

        :param id_proyecto: ID del proyecto al que se le importara el rol de proyecto
        :type id_proyecto: int

        :return: Renderiza la pagina para importar un rol de proyecto
        :rtype: HttpResponse
    """
    request_user = request.user

    # Verificamos que el usuario este autenticado
    if not request_user.is_authenticated:
        return HttpResponse('Usuario no autenticado', status=401)

    try:
        proyecto = Proyecto.objects.get(id=id_proyecto)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    # Verificacion que o es SrumMaster o es admin del sistema
    if not tiene_rol_en_proyecto(request_user, 'Scrum Master', proyecto):
        return HttpResponse('No tiene permisos para importar roles de proyecto', status=403)

    if request.method == 'POST':
        # id_proyecto: Proyecto a donde se VA A IMPORTAR
        roles = []  # Lista de los id de los roles a importar
        proyecto_seleccionado = Proyecto.objects.get(id=int(request.POST.get('proyecto_seleccionado')))  # Proyecto de donde SE IMPORTA los roles
        for rol in proyecto_seleccionado.proyecto_rol.all():
            if request.POST.get(f'{rol.id}') != None:
                roles.append(rol)

        # Recorremos los roles y creamos nuevos roles con los mismos permisos
        for rol in roles:
            if rol.nombre not in RolProyecto.objects.filter(proyecto=id_proyecto).values_list('nombre', flat=True):
                # Creamos el rol
                rol_nuevo = RolProyecto()
                rol_nuevo.nombre = rol.nombre
                rol_nuevo.descripcion = rol.descripcion
                rol_nuevo.proyecto = Proyecto.objects.get(id=id_proyecto)
                rol_nuevo.save()

                # Traemos los permisos del rol
                permisos = PermisoProyecto.objects.filter(rol=rol)

                # Recorremos los permisos y los asignamos al rol
                for permiso in permisos:
                    # Agregamos el rol al permiso
                    permiso.rol.add(rol_nuevo)
                    permiso.save()

        return redirect(f'/proyectos/{id_proyecto}/roles/')

    else:
        proyectos = Proyecto.objects.exclude(id=id_proyecto)
        # proyecto_objetivo = Proyecto.objects.get(nombre = request.GET.get('proyectos'))
        if request.GET.get('proyectos'):  # Este es el GET cuando solicita ver los roles de proyectos de un proyecto en especifico
            proyecto = Proyecto.objects.get(nombre=request.GET.get('proyectos'))
            roles = RolProyecto.objects.filter(proyecto=proyecto)
        else:  # Este es el GET cuando se llama desde otra pagina
            if proyectos.count() == 0:
                return redirect('crear_proyecto')
            proyecto = proyectos[0]
            roles = RolProyecto.objects.filter(proyecto=proyectos[0])

    return render(request, 'proyectos/roles_proyecto/importar_rol.html', {'proyectos': proyectos, 'proyecto_seleccionado': proyecto, 'roles': roles, 'proyecto': proyecto})
