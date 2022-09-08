from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.forms import inlineformset_factory

from gestion_proyectos_agile.templatetags.tiene_rol_en import tiene_permiso_en_proyecto
from .forms import EtapaHistoriaUsuarioForm, TipoHistoriaUsuarioForm

from proyectos.models import Proyecto
from .models import EtapaHistoriaUsuario, TipoHistoriaUsusario


@never_cache
def tiposHistoriaUsario(request, proyecto_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/", status=401)

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    if not tiene_permiso_en_proyecto(request.user, "pro_crearTipoUS", proyecto):
        return HttpResponseRedirect("/", status=422)

    return render(request, 'tipos-us/base.html', {'tipos': TipoHistoriaUsusario.objects.all(), 'proyecto': proyecto})


@never_cache
def crear_tipoHistoriaUsuario(request, proyecto_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/", status=401)

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    if not tiene_permiso_en_proyecto(request.user, "pro_crearTipoUS", proyecto):
        return HttpResponseRedirect("/", status=422)

    status = 200
    formset_factory = inlineformset_factory(TipoHistoriaUsusario, EtapaHistoriaUsuario, form=EtapaHistoriaUsuarioForm, extra=1, can_delete=False)
    if request.method == 'POST':
        form = TipoHistoriaUsuarioForm(request.POST)
        formset = formset_factory(request.POST, instance=form.instance)
        if form.is_valid() and formset.is_valid():
            tipo = form.save(commit=False)
            tipo.proyecto = proyecto
            if tipo.nombre in [t.nombre for t in proyecto.tiposHistoriaUsuario.all()]:
                form.add_error('nombre', "Ya existe un tipo de historia de usuario con este nombre.")
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
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/", status=401)

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)
    try:
        tipo = TipoHistoriaUsusario.objects.get(id=tipo_id)
    except Proyecto.DoesNotExist:
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
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/", status=401)

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    if not tiene_permiso_en_proyecto(request.user, "pro_crearTipoUS", proyecto):
        return HttpResponseRedirect("/", status=422)

    status = 200
    formset_factory = inlineformset_factory(TipoHistoriaUsusario, EtapaHistoriaUsuario, form=EtapaHistoriaUsuarioForm, extra=1, can_delete=False)
    if request.method == 'POST':
        form = TipoHistoriaUsuarioForm(request.POST)
        formset = formset_factory(request.POST, instance=form.instance)
        if form.is_valid() and formset.is_valid():
            tipo = form.save(commit=False)
            tipo.proyecto = proyecto
            if tipo.nombre in [t.nombre for t in proyecto.tiposHistoriaUsuario.all()]:
                form.add_error('nombre', "Ya existe un tipo de historia de usuario con este nombre.")
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
    return render(request, 'tipo-us/editar.html', {'form': form, 'proyecto': proyecto}, status=status)
