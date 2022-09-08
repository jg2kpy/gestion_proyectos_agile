from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.forms import inlineformset_factory
from .forms import EtapaHistoriaUsuarioForm, TipoHistoriaUsuarioForm

from proyectos.models import Proyecto
from .models import EtapaHistoriaUsuario, TipoHistoriaUsusario


@never_cache
def tiposHistoriaUsario(request, id_proyecto):
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/", status=401)

    try:
        proyecto = Proyecto.objects.get(id=id_proyecto)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

    # TODO: Validar que el usuario tiene permiso en proyecto
    return render(request, 'tipos-us/base.html', {'tipo-us': TipoHistoriaUsusario.objects.all(), 'proyecto': proyecto})


@never_cache
def crear_tipoHistoriaUsuario(request, proyecto_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/", status=401)

    # TODO: Validar que el usuario tiene permiso en proyecto

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

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
                return HttpResponseRedirect(f"/proyectos/{proyecto.id}/tipos-historia-usuario/")
        else:
            form.add_error(None, "Hay errores en el formulario.")
            status = 422
        pass
    else:
        form = TipoHistoriaUsuarioForm()
        formset = formset_factory()
    return render(request, 'tipos-us/crear_tipo.html', {'historiaformset': formset, 'form': form, 'proyecto': proyecto}, status=status)


# @never_cache
# def eliminar_tipoHistoriaUsuario(request, id_proyecto):
#     if not request.user.is_authenticated:
#         return HttpResponseRedirect("/", status=401)

#     # TODO: Validar que el usuario tiene permiso en proyecto

#     try:
#         proyecto = Proyecto.objects.get(id=id_proyecto)
#     except Proyecto.DoesNotExist:
#         return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)

#     status = 200
#     if request.method == 'POST':
#         form = TipoHistoriaUsuarioEliminarForm(request.POST)
#         if form.is_valid():
#             return render(request, 'tipos-us/base.html', {'tipo-us': TipoHistoriaUsusario.objects.all(), 'proyecto': proyecto}, status=status)
#         else:
#             status = 422
#     else:
#         form = TipoHistoriaUsuarioEliminarForm()

#     return render(request, 'tipos-us/eliminar_us.html', {'form': form, 'proyecto': proyecto}, status=status)


# @never_cache
# def editar_tipoHistoriaUsuario(request, id_proyecto, id_tipo_us):
#     if not request.user.is_authenticated:
#         return HttpResponseRedirect("/", status=401)

#     try:
#         proyecto = Proyecto.objects.get(id=id_proyecto)
#     except Proyecto.DoesNotExist:
#         return render(request, '404.html', {'info_adicional': "No se encontró este proyecto."}, status=404)
#     try:
#         tipo_us = tipo_us
#     except TipoHistoriaUsusario.DoesNotExist:
#         return render(request, '404.html', {'info_adicional': "No se encontró este tipo de historia de usuario."}, status=404)

#     status = 200
#     if request.method == 'POST':
#         form = TipoHistoriaUsusarioForm(request.POST, instance=tipo_us)
#         if form.is_valid():
#             return render(request, 'tipos-us/base.html', {'tipo-us': TipoHistoriaUsusario.objects.all(), 'proyecto': proyecto}, status=status)
#         else:
#             status = 422
#     else:
#         form = TipoHistoriaUsusarioForm(tipo_us)
#     return render(request, 'tipo-us/editar.html', {'form': form, 'proyecto': proyecto}, status=status)
