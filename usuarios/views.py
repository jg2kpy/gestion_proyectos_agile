from django.shortcuts import render
from django.forms import ModelForm
from .models import Usuario


class UsuarioForm(ModelForm):
    class Meta:
        model = Usuario
        fields = ['email', 'first_name', 'last_name', 'direccion', 'telefono']


def perfil(request):

    if request.method == "POST":
        # reservado para cuando quiere editar su perfil
        pass

    return render(request, 'socialaccount/perfil.html', {})
