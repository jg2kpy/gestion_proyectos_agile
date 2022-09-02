from django.shortcuts import render
from django.forms import ModelForm
from .models import Usuario
from django.http import HttpResponseRedirect
from django.views.decorators.cache import never_cache


class UsuarioForm(ModelForm):
    class Meta:
        model = Usuario
        fields = ['email', 'first_name', 'last_name', 'direccion', 'telefono', 'avatar_url']

    def __init__(self, *args, **kwargs):
        super(UsuarioForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


@never_cache
def perfil(request):
    """
    Vista para el perfil de usuario con form para editar datos.
    """
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/", status=401)

    if request.method == "POST":
        form = UsuarioForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/perfil/')

    perfil_form = UsuarioForm(instance=request.user)
    return render(request, 'socialaccount/perfil.html', {"perfil_form": perfil_form})
