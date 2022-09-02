from django.shortcuts import render
from django.forms import ModelForm, TextInput
from .models import Usuario


class UsuarioForm(ModelForm):
    class Meta:
        model = Usuario
        fields = ['email', 'first_name', 'last_name', 'direccion', 'telefono', 'avatar_url']

    def __init__(self, *args, **kwargs):
        super(UsuarioForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


def perfil(request):

    if request.method == "POST":
        # reservado para cuando quiere editar su perfil
        pass

    perfil_form = UsuarioForm(instance=request.user)
    return render(request, 'socialaccount/perfil.html', {"perfil_form": perfil_form})
