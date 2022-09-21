from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from django.forms import inlineformset_factory

from gestion_proyectos_agile.templatetags.tiene_rol_en import tiene_permiso_en_proyecto
from usuarios.models import Usuario
from .forms import ComentarioForm, EtapaHistoriaUsuarioForm, HistoriaUsuarioEditarConUserForm, HistoriaUsuarioEditarForm, HistoriaUsuarioForm, TipoHistoriaUsuarioForm

from proyectos.models import Proyecto
from .models import Comentario, EtapaHistoriaUsuario, HistoriaUsuario, TipoHistoriaUsusario


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
        return HttpResponseRedirect("/", status=401)

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    if not tiene_permiso_en_proyecto(request.user, "pro_crearTipoUS", proyecto):
        return HttpResponseRedirect("/", status=422)

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
        return HttpResponseRedirect("/", status=401)

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    if not tiene_permiso_en_proyecto(request.user, "pro_crearTipoUS", proyecto):
        return HttpResponseRedirect("/", status=422)

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
                return HttpResponseRedirect(f"/tipo-historia-usuario/{proyecto.id}/")
        else:
            form.add_error(None, "Hay errores en el formulario.")
            status = 422
        pass
    else:
        form = TipoHistoriaUsuarioForm()
        formset = formset_factory()
    return render(request, 'tipos-us/crear_tipo.html', {'historiaformset': formset, 'form': form, 'proyecto': proyecto}, status=status)


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
        return HttpResponseRedirect("/", status=401)

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)
    try:
        tipo = TipoHistoriaUsusario.objects.get(id=tipo_id)
    except TipoHistoriaUsusario.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este tipo de historia de usuario."}, status=404)

    if not tiene_permiso_en_proyecto(request.user, "pro_eliminarTipoUS", proyecto):
        return HttpResponseRedirect("/", status=422)

    status = 200
    if request.method == 'POST':
        try:
            tipo = TipoHistoriaUsusario.objects.get(id=tipo_id)
            tipo.delete()
        except TipoHistoriaUsusario.DoesNotExist:
            pass
        status = 200
        return HttpResponseRedirect(f"/tipo-historia-usuario/{proyecto.id}/")

    return render(request, 'tipos-us/eliminar_tipo.html', {'tipo': tipo, 'proyecto': proyecto, }, status=status)


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
        return HttpResponseRedirect("/", status=422)

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
                return HttpResponseRedirect(f"/tipo-historia-usuario/{proyecto.id}/")
        else:
            form.add_error(None, "Hay errores en el formulario.")
            status = 422
        pass
    else:
        form = TipoHistoriaUsuarioForm(instance=tipo)
        formset = formset_factory(instance=tipo)
    return render(request, 'tipos-us/editar_tipo.html', {'historiaformset': formset, 'form': form, 'proyecto': proyecto}, status=status)


@ never_cache
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
        return HttpResponse('Usuario no autenticado', status=401)

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    if not tiene_permiso_en_proyecto(request_user, 'pro_importarTipoUS', proyecto):
        return HttpResponse('No tiene permisos para importar tipos de historias de usuario', status=403)

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

                return redirect(f'/tipo-historia-usuario/{proyecto_id}/')

            else:
                mensaje = 'Ya existe un tipo de historia de usuario con ese nombre'

    proyectos = Proyecto.objects.exclude(id=proyecto_id)
    if request.GET.get('proyectos'):
        proyecto_seleccionado = Proyecto.objects.get(
            nombre=request.GET.get('proyectos'))
        tipos = TipoHistoriaUsusario.objects.filter(proyecto=proyecto)
    elif proyectos.count() > 0:
        proyecto_seleccionado = proyectos[0]
        tipos = TipoHistoriaUsusario.objects.filter(proyecto=proyectos[0])
    else:
        tipos = None

    return render(request, 'tipos-us/importar_rol.html', {'proyectos': proyectos, 'proyecto_seleccionado': proyecto_seleccionado, 'tipos': tipos, 'proyecto': proyecto, "mensaje": mensaje})


@never_cache
def historiaUsuario(request, proyecto_id):
    """Obtener vista de tipos de historia de usuario

    :param request: HttpRequest
    :type request: HttpRequest
    :param proyecto_id: Id del proyecto del cual se quiere ver los tipos de historia de usuario
    :type proyecto_id: int
    :return: 401 si no esta logueado, 404 si no existe el proyecto, 403 si no tiene permisos, 200 con una tabla de los permisos si todo esta bien
    :rtype: HttpResponse
    """
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/", status=401)

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    if not proyecto.usuario.filter(id=request.user.id).exists():
        return HttpResponseRedirect("/", status=422)

    return render(request, 'historias/base.html', {'historias': HistoriaUsuario.objects.filter(proyecto=proyecto), 'proyecto': proyecto})


@never_cache
def crear_historiaUsuario(request, proyecto_id):
    """Obtener vista de crear tipo de historia de usuario

    :param request: HttpRequest
    :type request: HttpRequest
    :param proyecto_id: Id del proyecto del cual se quiere crear un tipo de historia de usuario
    :type proyecto_id: int
    :return: 401 si no esta logueado, 404 si no existe el proyecto, 403 si no tiene permisos, 422 con información adicional si el formulario no fue creado correctamente, 200 con un formulario para crear un tipo de historia de usuario si todo esta bien
    :rtype: HttpResponse
    """
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/", status=401)

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    if not tiene_permiso_en_proyecto(request.user, "pro_cargarUSalBacklog", proyecto):
        return HttpResponseRedirect("/", status=422)

    status = 200
    if request.method == 'POST':
        form = HistoriaUsuarioForm(request.POST)
        if form.is_valid():
            historia = form.save(commit=False)
            if historia.nombre in [h.nombre for h in proyecto.backlog.all()]:
                form.add_error(
                    'nombre', "Ya existe una historia de usuario con este nombre en este proyecto.")
                status = 422
            else:
                historia.proyecto = proyecto
                historia.save()
                status = 200
                return HttpResponseRedirect(f"/historia-usuario/{proyecto.id}/")
        else:
            form.add_error(None, "Hay errores en el formulario.")
            status = 422
    else:
        form = HistoriaUsuarioForm()
    return render(request, 'historias/crear_historia.html', {'form': form, 'proyecto': proyecto}, status=status)


@never_cache
def borrar_historiaUsuario(request, proyecto_id, historia_id):
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
        return HttpResponseRedirect("/", status=401)

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    if not tiene_permiso_en_proyecto(request.user, "pro_cancelarUS", proyecto):
        return HttpResponseRedirect("/", status=422)

    try:
        historia = HistoriaUsuario.objects.get(id=historia_id)
    except HistoriaUsuario.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró esta historia de usuario."}, status=404)

    status = 200
    if request.method == 'POST':
        try:
            historia.delete()
        except HistoriaUsuario.DoesNotExist:
            pass
        status = 200
        return HttpResponseRedirect(f"/historia-usuario/{proyecto.id}/")

    return render(request, 'historias/base.html', {'historias': HistoriaUsuario.objects.filter(proyecto=proyecto), 'proyecto': proyecto})


@never_cache
def editar_historiaUsuario(request, proyecto_id, historia_id):
    """Obtener vista de crear tipo de historia de usuario

    :param request: HttpRequest
    :type request: HttpRequest
    :param proyecto_id: Id del proyecto del cual se quiere crear un tipo de historia de usuario
    :type proyecto_id: int
    :return: 401 si no esta logueado, 404 si no existe el proyecto, 403 si no tiene permisos, 422 con información adicional si el formulario no fue creado correctamente, 200 con un formulario para crear un tipo de historia de usuario si todo esta bien
    :rtype: HttpResponse
    """
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/", status=401)

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    if not tiene_permiso_en_proyecto(request.user, "pro_modificarUS", proyecto):
        return HttpResponseRedirect("/", status=422)

    try:
        historia = HistoriaUsuario.objects.get(id=historia_id)
    except HistoriaUsuario.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró esta historia de usuario."}, status=404)

    status = 200
    if request.method == 'POST':
        form = HistoriaUsuarioEditarConUserForm(request.POST)
        if form.is_valid():

            historia.descripcion = form.cleaned_data['descripcion']
            historia.bv = form.cleaned_data['bv']
            historia.up = form.cleaned_data['up']

            if form.cleaned_data['usuarioAsignado'] != None:
                historia.usuarioAsignado = form.cleaned_data['usuarioAsignado']

            historia.save()

            return HttpResponseRedirect(f"/historia-usuario/{proyecto.id}/")
        else:
            form.add_error(None, "Hay errores en el formulario.")
            status = 422
    else:

        if not tiene_permiso_en_proyecto(request.user, "pro_cambiarUsuarioAsignadoUS", proyecto):
            form = HistoriaUsuarioEditarForm(initial={
                                             'nombre': historia.nombre, 'descripcion': historia.descripcion, 'bv': historia.bv, 'up': historia.up})
        else:
            form = HistoriaUsuarioEditarConUserForm(initial={'nombre': historia.nombre, 'descripcion': historia.descripcion,
                                                    'bv': historia.bv, 'up': historia.up, 'usuarioAsignado': historia.usuarioAsignado})
    return render(request, 'historias/editar_historia.html', {'form': form, 'proyecto': proyecto, 'historia': historia}, status=status)


@never_cache
def comentarios_historiaUsuario(request, proyecto_id, historia_id):
    """Obtener vista de crear tipo de historia de usuario

    :param request: HttpRequest
    :type request: HttpRequest
    :param proyecto_id: Id del proyecto del cual se quiere crear un tipo de historia de usuario
    :type proyecto_id: int
    :return: 401 si no esta logueado, 404 si no existe el proyecto, 403 si no tiene permisos, 422 con información adicional si el formulario no fue creado correctamente, 200 con un formulario para crear un tipo de historia de usuario si todo esta bien
    :rtype: HttpResponse
    """
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/", status=401)

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

            comentario = Comentario(
                contenido=form.cleaned_data['contenido'], historiaUsuario=historia, usuario=request.user)

            comentario.save()

            return HttpResponseRedirect(f"/historia-usuario/comentarios/{proyecto.id}/{historia.id}/")
        else:
            form.add_error(None, "Hay errores en el formulario.")
            status = 422
    else:
        form = ComentarioForm()
    return render(request, 'historias/comentarios.html', {'form': form, 'proyecto': proyecto, 'historia': historia, 'comentarios': historia.comentarios.all()}, status=status)
