import datetime
from django.shortcuts import render, redirect
from django.forms import inlineformset_factory
from django.views.decorators.cache import never_cache
from django.db import models
import pytz
from gestion_proyectos_agile.views import crearNotificacion


from proyectos.models import Feriado, Proyecto
from proyectos.views import generarBurndownChart, generarVelocityChart
from .models import *
from gestion_proyectos_agile.templatetags.gpa_tags import tiene_permiso_en_proyecto, tiene_rol_en_proyecto
from .forms import ComentarioForm, EtapaHistoriaUsuarioForm, HistoriaUsuarioEditarForm, HistoriaUsuarioForm, SubirArchivoForm, TareaForm, TipoHistoriaUsuarioForm


@never_cache
def tiposHistoriaUsuario(request, proyecto_id):
    """Obtener vista de tipos de historia de usuario

    :param request: HttpRequest
    :type request: HttpRequest
    :param proyecto_id: Id del proyecto del cual se quiere ver los tipos de historia de usuario
    :type proyecto_id: int
    :return: 401 si no esta logueado, 404 si no existe el proyecto, 403 si no tiene permisos, 200 con una tabla de los permisos si todo esta bien
    :rtype: HttpResponse
    """
    if not request.user.is_authenticated:
        return render(request, '401.html', status=401)

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    if not tiene_permiso_en_proyecto(request.user, "pro_crearTipoUS", proyecto):
        return render(request, '403.html', {'info_adicional': 'No tiene permisos para gestionar tipos de historias de usuario'}, status=403)

    request.session['cancelar_volver_a'] = request.path
    return render(request, 'tipos-us/base.html', {'tipos': TipoHistoriaUsusario.objects.filter(proyecto=proyecto), 'proyecto': proyecto})


@never_cache
def crear_tipoHistoriaUsuario(request, proyecto_id):
    """Obtener vista de crear tipo de historia de usuario

    :param request: HttpRequest
    :type request: HttpRequest
    :param proyecto_id: Id del proyecto del cual se quiere crear un tipo de historia de usuario
    :type proyecto_id: int
    :return: 401 si no esta logueado, 404 si no existe el proyecto, 403 si no tiene permisos, 422 con información adicional si el formulario no fue creado correctamente, 200 con un formulario para crear un tipo de historia de usuario si todo esta bien
    :rtype: HttpResponse
    """
    if not request.user.is_authenticated:
        return render(request, '401.html', status=401)

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    if not tiene_permiso_en_proyecto(request.user, "pro_crearTipoUS", proyecto):
        return render(request, '403.html', {'info_adicional': 'No tiene permisos para crear tipos de historias de usuario'}, status=403)

    status = 200
    formset_factory = inlineformset_factory(
        TipoHistoriaUsusario, EtapaHistoriaUsuario, form=EtapaHistoriaUsuarioForm, extra=1, can_delete=False)
    if request.method == 'POST':
        form = TipoHistoriaUsuarioForm(request.POST)
        formset = formset_factory(request.POST, instance=form.instance)
        if form.is_valid() and formset.is_valid():
            tipo = form.save(commit=False)
            tipo.proyecto = proyecto
            if tipo.nombre in [t.nombre for t in proyecto.tiposHistoriaUsuario.all()]:
                form.add_error(
                    'nombre', "Ya existe un tipo de historia de usuario con este nombre.")
                status = 422
            elif '' in [e.instance.nombre for e in formset]:
                form.add_error(None, "No puede haber etapas sin nombre.")
                status = 422
            else:
                tipo.save()
                for i, etapa_form in enumerate(formset):
                    etapa = etapa_form.save(commit=False)
                    etapa.orden = i
                    etapa.save()
                status = 200
                return redirect('tiposHistoriaUsuario', proyecto_id=proyecto_id)
        else:
            form.add_error(None, "Hay errores en el formulario.")
            status = 422
        pass
    else:
        form = TipoHistoriaUsuarioForm()
        formset = formset_factory()

    volver_a = request.session['cancelar_volver_a']
    return render(request, 'tipos-us/crear_tipo.html', {"volver_a": volver_a, 'historiaformset': formset, 'form': form, 'proyecto': proyecto}, status=status)


@never_cache
def borrar_tipoHistoriaUsuario(request, proyecto_id, tipo_id):
    """Obtener vista de borrar tipo de historia de usuario

    :param request: HttpRequest
    :type request: HttpRequest
    :param proyecto_id: Id del proyecto del cual se quiere borrar un tipo de historia de usuario
    :type proyecto_id: int
    :param tipo_id: Id del tipo de historia de usuario que se quiere borrar
    :type tipo_id: int
    :return: 401 si no esta logueado, 404 si no existe el proyecto, 403 si no tiene permisos, 422 con información adicional si el formulario no fue creado correctamente, 200 con un formulario para borrar un tipo de historia de usuario si todo esta bien
    :rtype: HttpResponse
    """
    if not request.user.is_authenticated:
        return render(request, '401.html', status=401)

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)
    try:
        tipo = TipoHistoriaUsusario.objects.get(id=tipo_id)
    except TipoHistoriaUsusario.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este tipo de historia de usuario."}, status=404)

    if not tiene_permiso_en_proyecto(request.user, "pro_eliminarTipoUS", proyecto):
        return render(request, '403.html', {'info_adicional': 'No tiene permisos para eliminar tipos de historias de usuario'}, status=403)

    status = 200
    if request.method == 'POST':
        try:
            tipo = TipoHistoriaUsusario.objects.get(id=tipo_id)
            tipo.delete()
        except TipoHistoriaUsusario.DoesNotExist:
            pass 
        status = 200
        return redirect(request.session['cancelar_volver_a'] or 'tiposHistoriaUsuario', proyecto_id=proyecto_id)

    volver_a = request.session['cancelar_volver_a']
    return redirect(request.session['cancelar_volver_a'] or 'tiposHistoriaUsuario', proyecto_id=proyecto_id)


@never_cache
def editar_tipoHistoriaUsuario(request, proyecto_id, tipo_id):
    """Editar tipo de historia de usuario

    :param request: HttpRequest
    :type request: HttpRequest
    :param proyecto_id: Id del proyecto del cual se quiere editar un tipo de historia de usuario
    :type proyecto_id: int
    :param tipo_id: Id del tipo de historia de usuario que se quiere editar
    :type tipo_id: int
    :return: 401 si no esta logueado, 404 si no existe el proyecto, 403 si no tiene permisos, 422 con información adicional si el formulario no fue creado correctamente, 200 con un formulario para editar un tipo de historia de usuario si todo esta bien
    """
    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)
    try:
        tipo = TipoHistoriaUsusario.objects.get(id=tipo_id)
    except TipoHistoriaUsusario.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este tipo de historia de usuario."}, status=404)

    if not tiene_permiso_en_proyecto(request.user, "pro_crearTipoUS", proyecto):
        return render(request, '403.html', {'info_adicional': 'No tiene permisos para editar tipos de historias de usuario'}, status=403)

    status = 200
    formset_factory = inlineformset_factory(
        TipoHistoriaUsusario, EtapaHistoriaUsuario, form=EtapaHistoriaUsuarioForm, extra=0, can_delete=False)
    if request.method == 'POST':
        form = TipoHistoriaUsuarioForm(request.POST, instance=tipo)
        formset = formset_factory(request.POST, instance=form.instance)
        if form.is_valid() and formset.is_valid():
            tipo = form.save(commit=False)
            tipo.proyecto = proyecto
            tipo.id = tipo_id
            if '' in [e.instance.nombre for e in formset]:
                form.add_error(None, "No puede haber etapas sin nombre.")
                status = 422
            else:
                tipo.save()
                for i, etapa_form in enumerate(formset):
                    etapa = etapa_form.save(commit=False)
                    if EtapaHistoriaUsuario.objects.filter(TipoHistoriaUsusario=tipo, orden=i).exists():
                        etapa.id = EtapaHistoriaUsuario.objects.get(
                            TipoHistoriaUsusario=tipo, orden=i).id
                    etapa.orden = i
                    etapa.save()
                for i in range(len(formset), tipo.etapas.count()):
                    EtapaHistoriaUsuario.objects.get(
                        TipoHistoriaUsusario=tipo, orden=i).delete()

                status = 200
                return redirect('tiposHistoriaUsuario', proyecto_id=proyecto_id)
        else:
            form.add_error(None, "Hay errores en el formulario.")
            status = 422
        pass
    else:
        form = TipoHistoriaUsuarioForm(instance=tipo)
        formset = formset_factory(instance=tipo)

    volver_a = request.session['cancelar_volver_a']
    return render(request, 'tipos-us/editar_tipo.html', {"volver_a": volver_a, 'historiaformset': formset, 'form': form, 'proyecto': proyecto}, status=status)


@never_cache
def importar_tipoUS(request, proyecto_id):
    """
        Importar tipo de historia de usuario desde otro proyecto

        :param request: Peticion HTTP donde se recibe la informacion del tipo de historia de usuario a importar
        :type request: HttpRequest

        :param proyecto_id: ID del proyecto al que se le importara el tipo de historia de usuario
        :type proyecto_id: int

        :return: Renderiza la pagina para importar un tipo de historia
        :rtype: HttpResponse
    """
    request_user = request.user

    if not request_user.is_authenticated:
        return render(request, '401.html', status=401)

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    if not tiene_permiso_en_proyecto(request_user, 'pro_importarTipoUS', proyecto):
        return render(request, '403.html', {'info_adicional': 'No tiene permisos para importar tipos de historias de usuario'}, status=403)

    mensaje = None
    if request.method == 'POST':
        tipos = []
        proyecto_seleccionado = Proyecto.objects.get(
            id=int(request.POST.get('proyecto_seleccionado')))
        for tipoUS in proyecto_seleccionado.tiposHistoriaUsuario.all():
            if request.POST.get(f'{tipoUS.id}') != None:
                tipos.append(tipoUS)

        for tipoUS in tipos:
            if tipoUS.nombre not in TipoHistoriaUsusario.objects.filter(proyecto=proyecto_id).values_list('nombre', flat=True):
                tipoUS_nuevo = TipoHistoriaUsusario()
                tipoUS_nuevo.nombre = tipoUS.nombre
                tipoUS_nuevo.descripcion = tipoUS.descripcion
                tipoUS_nuevo.proyecto = proyecto
                tipoUS_nuevo.save()

                for etapa in tipoUS.etapas.all():
                    etapa_nueva = EtapaHistoriaUsuario()
                    etapa_nueva.nombre = etapa.nombre
                    etapa_nueva.descripcion = etapa.descripcion
                    etapa_nueva.orden = etapa.orden
                    etapa_nueva.TipoHistoriaUsusario = tipoUS_nuevo
                    etapa_nueva.save()

            else:
                mensaje = 'Ya existe un tipo de historia de usuario con ese nombre'

        if not mensaje:
            return redirect('tiposHistoriaUsuario', proyecto_id=proyecto_id)

    proyectos = Proyecto.objects.exclude(id=proyecto_id)
    if request.GET.get('proyectos'):
        proyecto_seleccionado = Proyecto.objects.get(
            nombre=request.GET.get('proyectos'))
        tipos = TipoHistoriaUsusario.objects.filter(proyecto=proyecto_seleccionado)
    elif proyectos.count() > 0:
        proyecto_seleccionado = proyectos[0]
        tipos = TipoHistoriaUsusario.objects.filter(proyecto=proyecto_seleccionado)
    else:
        proyecto_seleccionado = None
        tipos = None
    
    if tipos:
        tiposPropios = TipoHistoriaUsusario.objects.filter(proyecto=proyecto_id).values_list('nombre', flat=True)
        tipos = tipos.exclude(nombre__in=tiposPropios)

    volver_a = request.session['cancelar_volver_a']
    return render(request, 'tipos-us/importar_tipo.html', {"volver_a": volver_a, 'proyectos': proyectos, 'proyecto_seleccionado': proyecto_seleccionado, 'tipos': tipos, 'proyecto': proyecto, "mensaje": mensaje})

def moverEtapa(request, proyecto_id, historia_id):
    """
    Mover historia de usuario a la siguiente etapa

    :param request: HttpRequest
    :type request: HttpRequest
    :param proyecto_id: Id del proyecto del cual se quiere pasar las historia de usuario a la siguiente etapa
    :type proyecto_id: int
    :param proyecto_id: Id de la historia de usuario de la cual se quiere pasar a la siguiente etapa
    :type proyecto_id: int
    :return: 401 si no esta logueado, 404 si no existe el proyecto o historia de usuario, 422 si no tiene rol necesario en proyecto
    :rtype: HttpResponse
    """
    status = 200

    if not request.user.is_authenticated:
        return render(request, '401.html', status=401)

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    try:
        historia = HistoriaUsuario.objects.get(id=historia_id)
    except HistoriaUsuario.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró la historia de usuario."}, status=404)

    if not tiene_rol_en_proyecto(request.user, "Scrum Master", proyecto) and not historia.usuarioAsignado == request.user:
        return render(request, '403.html', {'info_adicional': 'No tiene permisos para mover historias de usuario'}, status=403)

    if request.method == 'POST':
        historia.guardarConHistorial()
        if 'siguiente' in request.POST:

            if historia.tareas.filter(etapa=historia.etapa).count() <= 0:
                return render(request, '404.html', {'info_adicional': "No se puede pasar a la siguiente etapa porque no existen tareas en esta etapa."}, status=422)

            sigOrden = historia.etapa.orden + 1 if historia.etapa else 0
            if sigOrden == historia.tipo.etapas.count():
                historia.estado = HistoriaUsuario.Estado.TERMINADO

                if historia.usuarioAsignado:
                    crearNotificacion(
                        historia.usuarioAsignado,
                        f"La historia de usuario {historia.nombre} perteneciente al sprint {historia.sprint.nombre} dentro del proyecto {historia.proyecto.nombre} pasa a estado Terminado"
                    )

            else:
                sigEtapa = EtapaHistoriaUsuario.objects.get(
                    orden=sigOrden, TipoHistoriaUsusario=historia.tipo)
                historia.etapa = sigEtapa

                if historia.usuarioAsignado:
                    crearNotificacion(
                        historia.usuarioAsignado,
                        f"La historia de usuario {historia.nombre} perteneciente al sprint {historia.sprint.nombre} dentro del proyecto {historia.proyecto.nombre} pasó a etapa {historia.etapa.nombre}"
                    )
        else:
            antOrden = historia.etapa.orden - 1 if historia.etapa and historia.etapa.orden > 1 else 0

            antEtapa = EtapaHistoriaUsuario.objects.get(
                orden=antOrden, TipoHistoriaUsusario=historia.tipo)
            if historia.etapa != antEtapa:
                for trabajo in historia.tareas.all():
                    trabajo.considerado = True
                    trabajo.save()
                historia.etapa = antEtapa

                if historia.usuarioAsignado:
                    crearNotificacion(
                        historia.usuarioAsignado,
                        f"La historia de usuario {historia.nombre} perteneciente al sprint {historia.sprint.nombre} dentro del proyecto {historia.proyecto.nombre} volvió a etapa {historia.etapa.nombre}"
                    )
    
        historia.save()

        return redirect(request.session['cancelar_volver_a'] or 'historiaUsuarioBacklog', proyecto_id)

    request.session['cancelar_volver_a'] = request.path
    return render(request, '404.html', {'info_adicional': "No se encontró la historia de usuario."}, status=404)


@never_cache
def historiaUsuarioBacklog(request, proyecto_id):
    """Obtener vista del backlog

    :param request: HttpRequest
    :type request: HttpRequest
    :param proyecto_id: Id del proyecto del cual se quiere ver las historia de usuario
    :type proyecto_id: int
    :return: 401 si no esta logueado, 404 si no existe el proyecto, 403 si no tiene permisos, 200 con la tabla del backlog
    :rtype: HttpResponse
    """
    if not request.user.is_authenticated:
        return render(request, '401.html', status=401)

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    if not proyecto.usuario.filter(id=request.user.id).exists():
        return render(request, '403.html', {'info_adicional': 'No pertenece a este proyecto, no tiene permisos para ver este backlog'}, status=403)

    request.session['cancelar_volver_a'] = request.path
    return render(request, 'historias/base.html', {'historias': HistoriaUsuario.objects.filter(proyecto=proyecto, estado=HistoriaUsuario.Estado.ACTIVO).order_by('nombre'), 'proyecto': proyecto, 'esBacklog': True, 'titulo': 'Backlog'})


@never_cache
def historiaUsuarioCancelado(request, proyecto_id):
    """Obtener vista de la lista de historias de usuario canceladas

    :param request: HttpRequest
    :type request: HttpRequest
    :param proyecto_id: Id del proyecto del cual se quiere ver las historia de usuario canceladas
    :type proyecto_id: int
    :return: 401 si no esta logueado, 404 si no existe el proyecto, 403 si no tiene permisos, 200 con la tabla de historias de usuario canceladas
    :rtype: HttpResponse
    """
    if not request.user.is_authenticated:
        return render(request, '401.html', status=401)

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    if not proyecto.usuario.filter(id=request.user.id).exists():
        return render(request, '403.html', {'info_adicional': 'No pertenece a este proyecto, no tiene permisos para ver estas historias canceladas'}, status=403)

    request.session['cancelar_volver_a'] = request.path
    return render(request, 'historias/base.html', {'historias': HistoriaUsuario.objects.filter(proyecto=proyecto, estado=HistoriaUsuario.Estado.CANCELADO).order_by('nombre'), 'proyecto': proyecto, 'titulo': 'Historias Canceladas'})


@never_cache
def historiaUsuarioTerminado(request, proyecto_id):
    """Obtener vista de historias de usuario terminadas

    :param request: HttpRequest
    :type request: HttpRequest
    :param proyecto_id: Id del proyecto del cual se quiere ver las historia de usuario teminadas
    :type proyecto_id: int
    :return: 401 si no esta logueado, 404 si no existe el proyecto, 403 si no tiene permisos, 200 con la tabla de historias de usuario terminadas
    :rtype: HttpResponse
    """
    if not request.user.is_authenticated:
        return render(request, '401.html', status=401)

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    if not proyecto.usuario.filter(id=request.user.id).exists():
        return render(request, '403.html', {'info_adicional': 'No pertenece a este proyecto, no tiene permisos para ver estas historias terminadas'}, status=403)

    request.session['cancelar_volver_a'] = request.path
    return render(request, 'historias/base.html', {'historias': HistoriaUsuario.objects.filter(proyecto=proyecto, estado=HistoriaUsuario.Estado.TERMINADO).order_by('nombre'), 'proyecto': proyecto, 'titulo': 'Historias Terminadas'})


@never_cache
def historiaUsuarioAsignado(request, proyecto_id):
    """Obtener vista de historias de usuario asignados al usuario que realiza la peticion

    :param request: HttpRequest
    :type request: HttpRequest
    :param proyecto_id: Id del proyecto del cual se quiere ver las historia de usuario asignadas a este usuario
    :type proyecto_id: int
    :return: 401 si no esta logueado, 404 si no existe el proyecto, 403 si no tiene permisos, 200 con la tabla de historias de usuario asignadas a este usuario
    :rtype: HttpResponse
    """
    if not request.user.is_authenticated:
        return render(request, '401.html', status=401)

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    if not proyecto.usuario.filter(id=request.user.id).exists():
        return render(request, '403.html', {'info_adicional': 'No pertenece a este proyecto, no tiene permisos para ver estas historias'}, status=403)

    request.session['cancelar_volver_a'] = request.path
    return render(request, 'historias/base.html', {'historias': HistoriaUsuario.objects.filter(proyecto=proyecto, estado=HistoriaUsuario.Estado.ACTIVO, usuarioAsignado=request.user).order_by('nombre'), 'proyecto': proyecto, 'titulo': 'Mis Historias'})


@never_cache
def crear_historiaUsuario(request, proyecto_id):
    """Obtener vista de crear una historia de usuario

    :param request: HttpRequest
    :type request: HttpRequest
    :param proyecto_id: Id del proyecto del cual se quiere crear una de historia de usuario
    :type proyecto_id: int
    :return: 401 si no esta logueado, 404 si no existe el proyecto, 403 si no tiene permisos, 422 con información adicional si el formulario no fue creado correctamente, 200 con un formulario para crear una historia de usuario si todo esta bien
    :rtype: HttpResponse
    """
    if not request.user.is_authenticated:
        return render(request, '401.html', status=401)

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    if not tiene_permiso_en_proyecto(request.user, "pro_cargarUSalBacklog", proyecto) and not tiene_permiso_en_proyecto(request.user, "pro_verproyecto", proyecto):
        return render(request, '403.html', {'info_adicional': 'No tiene permisos para cargar una historia de usuario al backlog'}, status=403)

    status = 200
    if request.method == 'POST':
        form = HistoriaUsuarioForm(request.POST)
        archivoForm = SubirArchivoForm(request.POST, request.FILES)

        if form.is_valid():
            historia = form.save(commit=False)
            if historia.nombre in [h.nombre for h in proyecto.backlog.all()]:
                form.add_error(
                    'nombre', "Ya existe una historia de usuario con este nombre en este proyecto.")
                status = 422
            else:
                historia.proyecto = proyecto
                historia.etapa = None

                historia.save()
                archivosSubidos = request.FILES.getlist('archivo')
                if archivoForm.is_valid():

                    for archivoSubido in archivosSubidos:
                        nuevoArchivo = ArchivoAnexo(nombre=archivoSubido.name, subido_por=request.user, archivo=archivoSubido)
                        nuevoArchivo.save()
                        historia.archivos.add(nuevoArchivo)
                
                status = 200
                return redirect(request.session['cancelar_volver_a'] or 'historiaUsuarioBacklog', proyecto_id=proyecto_id)
        else:
            form.add_error(None, "Hay errores en el formulario.")
            status = 422
    else:
        form = HistoriaUsuarioForm()
        archivoForm = SubirArchivoForm()
        tipos = [(tipo.id, tipo.nombre) for tipo in proyecto.tiposHistoriaUsuario.all()]
        form.set_tipos(tipos)
        if tiene_permiso_en_proyecto(request.user, "pro_verproyecto", proyecto):
            form.fields['up'].widget.attrs['readonly'] = True

    volver_a = request.session['cancelar_volver_a']
    return render(request, 'historias/crear_historia.html', {"volver_a": volver_a, 'form': form, 'archivo_form': archivoForm, 'proyecto': proyecto}, status=status)


@never_cache
def borrar_historiaUsuario(request, proyecto_id, historia_id):
    """Obtener vista de cancelar una historia de usuario

    :param request: HttpRequest
    :type request: HttpRequest
    :param proyecto_id: Id del proyecto del cual se quiere cancelar una historia de usuario
    :type proyecto_id: int
    :param tipo_id: Id del tipo de historia de usuario que se quiere borrar
    :type tipo_id: int
    :return: 401 si no esta logueado, 404 si no existe el proyecto, 403 si no tiene permisos, 422 con información adicional si el formulario no fue creado correctamente, 200 indicando que se logro cancelar correctamente
    :rtype: HttpResponse
    """
    if not request.user.is_authenticated:
        return render(request, '401.html', status=401)

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    if not tiene_permiso_en_proyecto(request.user, "pro_cancelarUS", proyecto):
        return render(request, '403.html', {'info_adicional': 'NO tiene permisos para cancelar una historia de usuario'}, status=403)

    try:
        historia = HistoriaUsuario.objects.get(id=historia_id)
    except HistoriaUsuario.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró esta historia de usuario."}, status=404)

    status = 200
    if request.method == 'POST':
        try:
            historia.estado = HistoriaUsuario.Estado.CANCELADO
            historia.save()

            if historia.usuarioAsignado:
                crearNotificacion(
                    historia.usuarioAsignado,
                    f"La historia de usuario {historia.nombre} dentro del proyecto {historia.proyecto.nombre} pasa a estado Cancelado"
                )
        except HistoriaUsuario.DoesNotExist:
            pass
        status = 200
        return redirect(request.session['cancelar_volver_a'] or 'historiaUsuarioBacklog', proyecto_id=proyecto_id)

    volver_a = request.session['cancelar_volver_a']
    return render(request, 'historias/base.html', {"volver_a": volver_a, 'historias': HistoriaUsuario.objects.filter(proyecto=proyecto), 'proyecto': proyecto}, status=status)


@never_cache
def editar_historiaUsuario(request, proyecto_id, historia_id):
    """Obtener vista de editar una historia de usuario

    :param request: HttpRequest
    :type request: HttpRequest
    :param proyecto_id: Id del proyecto del cual se quiere editar una historia de usuario
    :type proyecto_id: int
    :return: 401 si no esta logueado, 404 si no existe el proyecto, 403 si no tiene permisos, 422 con información adicional si el formulario no fue creado correctamente, 200 con un formulario para editar una historia de usuario si todo esta bien
    :rtype: HttpResponse
    """
    if not request.user.is_authenticated:
        return render(request, '401.html', status=401)

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    if not tiene_permiso_en_proyecto(request.user, "pro_modificarUS", proyecto):
        return render(request, '403.html', {'info_adicional': 'NO tiene permisos para modificar una historia de usuario'}, status=403)

    try:
        historia = HistoriaUsuario.objects.get(id=historia_id)
    except HistoriaUsuario.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró esta historia de usuario."}, status=404)

    status = 200
    if request.method == 'POST':
        form = HistoriaUsuarioEditarForm(request.POST)
        if form.is_valid():
            historia.guardarConHistorial()
            historia.descripcion = form.cleaned_data['descripcion']
            historia.bv = form.cleaned_data['bv']
            historia.up = form.cleaned_data['up']

            historia.save()

            if historia.usuarioAsignado:
                crearNotificacion(
                    historia.usuarioAsignado,
                    f"La historia de usuario {historia.nombre} dentro del proyecto {historia.proyecto.nombre} fué editada"
                )

            return redirect(request.session['cancelar_volver_a'] or 'historiaUsuarioBacklog', proyecto_id=proyecto_id)
        else:
            form.add_error(None, "Hay errores en el formulario.")
            status = 422
    else:
        form = HistoriaUsuarioEditarForm(initial={'nombre': historia.nombre, 'descripcion': historia.descripcion,
                                                  'bv': historia.bv, 'up': historia.up})
        
    volver_a = request.session['cancelar_volver_a']
    return render(request, 'historias/editar_historia.html', {'form': form, 'proyecto': proyecto, 'historia': historia, "volver_a": volver_a}, status=status)


@never_cache
def comentarios_historiaUsuario(request, proyecto_id, historia_id):
    """Obtener vista de ver y realizar comentarios a una historia de usuario

    :param request: HttpRequest
    :type request: HttpRequest
    :param proyecto_id: Id del proyecto del cual se quiere leer comentarios o crear un comentario
    :type proyecto_id: int
    :param historia_id: Id de la historia de usuario que se quiere tener acceso a sus comentarios
    :type historia_id: int
    :return: 401 si no esta logueado, 404 si no existe el proyecto, 403 si no tiene permisos, 422 con información adicional si el formulario no fue creado correctamente, 200 con la lista de los comentarios y un formulario para crear un comentario si todo esta bien
    :rtype: HttpResponse
    """
    if not request.user.is_authenticated:
        return render(request, '401.html', status=401)

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    try:
        historia = HistoriaUsuario.objects.get(id=historia_id)
    except HistoriaUsuario.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró esta historia de usuario."}, status=404)

    status = 200
    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():

            comentario = Comentario()
            comentario.usuario = request.user
            comentario.contenido = form.cleaned_data['contenido']
            comentario.save()
            historia.comentarios.add(comentario)

            if historia.usuarioAsignado:
                crearNotificacion(
                    historia.usuarioAsignado,
                    f"El usuario {request.user.email} ha hecho un comentario en la historia de usuario {historia.nombre} perteneciente al sprint {historia.sprint.nombre} dentro del proyecto {historia.proyecto.nombre}"
                )
            return redirect('comentarios_historiaUsuario', proyecto_id=proyecto_id, historia_id=historia.id)
        else:
            form.add_error(None, "Hay errores en el formulario.")
            status = 422
    else:
        form = ComentarioForm()

    volver_a = request.session['cancelar_volver_a']
    return render(request, 'historias/comentarios.html', {'form': form, 'proyecto': proyecto, 'historia': historia, 'comentarios': historia.comentarios.all(), "volver_a": volver_a}, status=status)

@never_cache
def tareas(request, proyecto_id, historia_id):
    """Obtener vista de ver y guardar trabajos de una historia de usuario

    :param request: HttpRequest
    :type request: HttpRequest
    :param proyecto_id: Id del proyecto del cual se quiere leer comentarios o crear un comentario
    :type proyecto_id: int
    :param historia_id: Id de la historia de usuario que se quiere tener acceso a sus comentarios
    :type historia_id: int
    :return: 401 si no esta logueado, 404 si no existe el proyecto, 403 si no tiene permisos, 422 con información adicional si el formulario no fue creado correctamente, 200 con la lista de los comentarios y un formulario para crear un comentario si todo esta bien
    :rtype: HttpResponse
    """
    if not request.user.is_authenticated:
        return render(request, '401.html', status=401)

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    try:
        historia = HistoriaUsuario.objects.get(id=historia_id)
    except HistoriaUsuario.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró esta historia de usuario."}, status=404)

    status = 200
    if request.method == 'POST':
        form = TareaForm(request.POST)
        if form.is_valid():

            tarea = Tarea()
            tarea.historia = historia
            tarea.usuario = request.user
            tarea.descripcion = form.cleaned_data['descripcion']
            tarea.horas = form.cleaned_data['horas']
            tarea.etapa = historia.etapa
            tarea.sprint = historia.sprint
            tarea.save()

            if historia.usuarioAsignado:
                crearNotificacion(
                    historia.usuarioAsignado,
                    f"El usuario {request.user.email} ha marcado {tarea.horas} horas de trabajo en la historia de usuario {historia.nombre} perteneciente al sprint {historia.sprint.nombre} dentro del proyecto {historia.proyecto.nombre}"
                )

            return redirect('tareas', proyecto_id=proyecto_id, historia_id=historia.id)
        else:
            form.add_error(None, "Hay errores en el formulario.")
            status = 422
    else:
        form = TareaForm()

    all_tareas = Tarea.objects.filter(historia=historia).order_by('-sprint__fecha_inicio', 'etapa__orden', '-fecha')
    sprints_tareas = {}
    for tarea in all_tareas:
        if tarea.sprint not in sprints_tareas:
            tarea.sprint.nombre_pantalla = ("actual" if tarea.sprint == historia.sprint else 
                tarea.sprint.nombre + " (" + tarea.sprint.fecha_inicio.strftime("%d/%m/%Y") + " - " + tarea.sprint.fecha_fin.strftime("%d/%m/%Y") + ")")
            tarea.sprint.tareaslist = []
            sprints_tareas[tarea.sprint] = tarea.sprint
        sprints_tareas[tarea.sprint].tareaslist.append(tarea)

    volver_a = request.session['cancelar_volver_a']
    return render(request, 'historias/tareas.html', {'form': form, 'proyecto': proyecto, 'historia': historia, 'sprints_tareas': sprints_tareas, "volver_a": volver_a}, status=status)

@never_cache
def restaurar_historia_historial(request, proyecto_id, historia_id):
    """
    Permite ver y restaurar versiones anteriores de una historia de usuario. La acción de restaurar a su vez se guarda otra vez en el historial.

    :param request: HttpRequest
    :type request: HttpRequest
    :param proyecto_id: Id del proyecto del cual se quiere crear un tipo de historia de usuario
    :type proyecto_id: int
    :param historia_id: Id de la historia de usuario de la cual se quiere visualizar el historial.
    :type historia_id: int
    :return: 401 si no esta logueado, 404 si no existe el proyecto, 403 si no tiene permisos, 422 con información adicional si el formulario no fue creado correctamente, 200 con un la lista de versiones anteriores en una tabla html en caso de éxito
    :rtype: HttpResponse
    """
    if not request.user.is_authenticated:
        return render(request, '401.html', status=401)

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    try:
        historia = HistoriaUsuario.objects.get(id=historia_id)
    except HistoriaUsuario.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró esta historia de usuario."}, status=404)
    
    if request.method == 'POST':
        try:
            versionPrevia = HistoriaUsuario.objects.get(id=request.POST.get('version'))
        except HistoriaUsuario.DoesNotExist:
            return render(request, '404.html', {'info_adicional': "No se encontró esta historia de usuario."}, status=404)

        if historia.usuarioAsignado:
            crearNotificacion(
                historia.usuarioAsignado,
                f"El usuario {request.user.email} ha restaurado la historia de usuario {historia.nombre} a la versión registrada \
                    en la fecha {versionPrevia.fecha_modificacion.strftime('%m/%d/%Y, %H:%M:%S')} dentro del proyecto {historia.proyecto.nombre}"
            )

        historia.restaurarDelHistorial(versionPrevia)

    volver_a = request.session['cancelar_volver_a']
    return render(request, 'historias/historial.html', {"volver_a": volver_a, 'proyecto': proyecto, 'version_ori': historia, 'versiones': historia.obtenerVersiones()}, status=200)


@ never_cache
def verTablero(request, proyecto_id, tipo_id):
    """
        Ver el tablero de tipo tipo_id en el proyecto proyecto_id

        :param request: Peticion HTTP donde se recibe la informacion
        :type request: HttpRequest

        :param proyecto_id: ID del proyecto del cual se quiere visualizar el tablero
        :type proyecto_id: int

        :param proyecto_id: ID del proyecto del cual se quiere visualizar el tablero
        :type proyecto_id: int

        :return: Renderiza el tablero del tipo de historia de usuario seleccionado
        :rtype: HttpResponse
    """

    if not request.user.is_authenticated:
        return render(request, '401.html', status=401)
        
    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    if not proyecto.usuario.filter(id=request.user.id).exists():
        return render(request, '403.html', {'info_adicional': 'No pertenece a este proyecto, no tiene permisos para ver tableros de tipos de historias de usuario en este proyecto'}, status=403)

    try:
        tipo = TipoHistoriaUsusario.objects.get(id=tipo_id)
    except TipoHistoriaUsusario.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este tipo de historia de usuario."}, status=404)

    if tipo.proyecto != proyecto:
        return render(request, '404.html', {'info_adicional': "No se encontró este tipo de historia de usuario."}, status=404)

    sprints = Sprint.objects.filter(proyecto=proyecto).exclude(fecha_inicio__isnull=True)
    sprintDesc = sprints.order_by("-fecha_inicio")
    sprintCookie = request.COOKIES.get(f'indiceActual_{proyecto.id}')
    sprintCookie = sprintCookie if sprintCookie and int(sprintCookie) < len(sprintDesc) else 0

    etapas = []

    if request.method == 'POST':
        if request.POST.get('sprintId'):
            sprintId = request.POST.get('sprintId')

            for etapa in tipo.etapas.all().order_by('orden'):
                aux_etapa = {"nombre": etapa.nombre, "historias": [], "proyecto": proyecto_id}
                
                if Sprint.objects.get(id=sprintId).estado == 'Desarrollo':
                    aux_etapa["historias"] = etapa.historias.filter(sprint__id=sprintId, estado='A')
                else:
                    aux_etapa["historias"] = etapa.historias.filter(sprint__id=sprintId, estado='S')
                
                etapas.append(aux_etapa)

        # Función para terminar un sprint
        if request.POST.get('terminar'):
            sprintTerminar = proyecto.sprints.get(estado="Desarrollo")
            sprintTerminar.estado = "Terminado"

            sprintTerminar.duracion = 0
            fecha_aux = sprintTerminar.fecha_inicio
            while fecha_aux <= sprintTerminar.fecha_fin:
                if not (fecha_aux.weekday() >= 5 or fecha_aux.date() in Feriado.objects.filter(proyecto=proyecto)):
                    sprintTerminar.duracion += 1
                fecha_aux += datetime.timedelta(days=1)
            sprintTerminar.fecha_fin = datetime.datetime.now(pytz.timezone('America/Asuncion'))
            sprintTerminar.save()

            usuariosSprint = Usuario.objects.filter(equipo__id=sprintTerminar.proyecto.id)
            
            for usuario in usuariosSprint:
                crearNotificacion(
                    usuario,
                    f"El sprint {sprintTerminar.nombre} perteneciente al proyecto {sprintTerminar.proyecto} pasa a estado Terminado"
                )

            usListFinalizar = HistoriaUsuario.objects.filter(proyecto=proyecto, sprint=sprintTerminar,estado=HistoriaUsuario.Estado.ACTIVO)
            
            for usFinalizar in usListFinalizar:
                id_ori = usFinalizar.id
                usFinalizar.sprint = None
                usFinalizar.save()
                copiaUs = usFinalizar
                copiaUs.pk = None
                copiaUs.sprint = sprintTerminar
                copiaUs.estado = 'S'
                copiaUs.save()
                # Volver a tener de base de dato para no apuntar a copia
                usFinalizar = HistoriaUsuario.objects.get(id=id_ori)
                usFinalizar.horasAsignadas = 0
                usFinalizar.usuarioAsignado = None
                usFinalizar.save()
                sprintInfo = SprintInfo()
                sprintInfo.sprint = sprintTerminar
                sprintInfo.historia = usFinalizar
                sprintInfo.versionEnHistorial = copiaUs
                sprintInfo.horasAsignadas = copiaUs.horasAsignadas
                sprintInfo.horasUsadas = sum([tarea.horas for tarea in Tarea.objects.filter(historia=id_ori, sprint=sprintTerminar)])
                sprintInfo.save()

            generarBurndownChart(sprintTerminar.id)
            generarVelocityChart(proyecto.id)
            
            proyecto.estado = "Planificación"
            proyecto.save()
            
    else:
        for etapa in tipo.etapas.all().order_by('orden'):
            aux_etapa = {"nombre": etapa.nombre, "historias": [], "proyecto": proyecto_id}
            
            if sprintCookie:
                if Sprint.objects.get(id=sprintDesc[int(sprintCookie)].id).estado == 'Desarrollo':
                    aux_etapa["historias"] = etapa.historias.filter(sprint__id=sprintDesc[int(sprintCookie)].id, estado=HistoriaUsuario.Estado.ACTIVO)
                else:
                    aux_etapa["historias"] = etapa.historias.filter(sprint__id=sprintDesc[int(sprintCookie)].id, estado=HistoriaUsuario.Estado.SNAPSHOT)

            else:    
                if Sprint.objects.get(id=sprintDesc[0].id).estado == 'Desarrollo':
                    aux_etapa["historias"] = etapa.historias.filter(sprint__id=sprintDesc[0].id, estado=HistoriaUsuario.Estado.ACTIVO)
                else:
                    aux_etapa["historias"] = etapa.historias.filter(sprint__id=sprintDesc[0].id, estado=HistoriaUsuario.Estado.SNAPSHOT)

            etapas.append(aux_etapa)
    
    request.session['cancelar_volver_a'] = request.path
    return render(request, 'tablero/tablero.html', {'etapas': etapas, "tipo": tipo, 'proyecto': proyecto, "sprints": sprintDesc})

@never_cache
def ver_archivos(request, proyecto_id, historia_id):
    """
    Permite ver los archivos de una historia de usuario.

    :param request: HttpRequest
    :type request: HttpRequest
    :rtype: HttpResponse
    """
    if not request.user.is_authenticated:
        return render(request, '401.html', status=401)

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    try:
        historia = HistoriaUsuario.objects.get(id=historia_id)
    except HistoriaUsuario.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró esta historia de usuario."}, status=404)

    if not proyecto.usuario.filter(id=request.user.id).exists():
        return render(request, '403.html', {'info_adicional': "No pertenece a este proyecto, no tiene permisos para ver estos archivos."}, status=403)

    status = 200
    archivoForm = SubirArchivoForm(request.POST, request.FILES)
    if request.method == 'POST':
        if request.POST.get('accion') == 'eliminar':
            try:
                archivo = ArchivoAnexo.objects.get(id=int(request.POST.get('archivo_id')))
            except ArchivoAnexo.DoesNotExist:
                return render(request, 'historias/archivos.html', {'proyecto': proyecto, 'historia': historia, 'archivos': historia.archivos.all()}, status=status)
            archivo.historia_usuario.get(estado=HistoriaUsuario.Estado.ACTIVO).guardarConHistorial()
            archivo.historia_usuario.get(estado=HistoriaUsuario.Estado.ACTIVO).archivos.remove(archivo)
            archivo.save()
            status = 200
        elif request.POST.get('accion') == 'subir':
            archivosSubidos = request.FILES.getlist('archivo')
            if archivoForm.is_valid():
                if len(archivosSubidos) > 0:
                    historia.guardarConHistorial()
                for archivoSubido in archivosSubidos:
                    nuevoArchivo = ArchivoAnexo(nombre=archivoSubido.name, subido_por=request.user, archivo=archivoSubido)
                    nuevoArchivo.save()
                    historia.archivos.add(nuevoArchivo)
                status = 200
            else:
                archivoForm.add_error(None, "El archivo no es válido.")
    
    volver_a = request.session['cancelar_volver_a']
    return render(request, 'historias/archivos.html', {'proyecto': proyecto, 'historia': historia, 'archivos': historia.archivos.all(), \
        "archivo_form": archivoForm, "titulo": f"Archivos anexos en '{historia.nombre}'", "volver_a": volver_a}, status=status)
