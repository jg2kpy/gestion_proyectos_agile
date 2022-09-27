from django import forms
from django.forms import ModelForm

from usuarios.models import Usuario
from .models import PermisoSistema, Usuario


class RolSistemaForm(forms.Form):
    """
        Formulario para crear un rol de sistema

        :param nombre: Nombre del rol de sistema
        :type nombre: Texto
        :param descripcion: Descripcion del rol de sistema
        :type descripcion: Texto
        :param permisos: Permisos del rol de sistema
        :type permisos: Lista de permisos

        :return: Formulario para crear un rol de sistema
        :rtype: Formulario
    """
    nombre = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    descripcion = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    permisos = forms.ModelMultipleChoiceField(queryset=None, widget=forms.CheckboxSelectMultiple())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['permisos'].queryset = PermisoSistema.objects.all()


class UsuarioForm(ModelForm):
    """
    Clase que representa el formulario de usuario. Ver Django ModelForm documentación para más información.
    """
    class Meta:
        model = Usuario
        fields = ['email', 'first_name', 'last_name', 'direccion', 'telefono', 'avatar_url']

    def __init__(self, *args, **kwargs):
        super(UsuarioForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})