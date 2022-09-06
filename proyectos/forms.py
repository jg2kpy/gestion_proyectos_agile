from django import forms
from usuarios.models import Usuario
from .models import Proyecto
# Traemos los roles y los permisos de los proyectos
from usuarios.models import RolProyecto, PermisoProyecto


# Estados de proyecto
ESTADOS_PROYECTO = (
    ('Planificacion', 'Planificacion'),
    ('Ejecucion', 'Ejecucion'),
    ('Finalizado', 'Finalizado'),
    ('Cancelado', 'Cancelado'),
    ('En espera', 'En espera'),
)


class ProyectoForm(forms.Form):
    nombre = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    descripcion = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    fecha_inicio = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control'}))
    fecha_fin = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control'}))
    scrum_master = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['scrum_master'].choices = [
            (usuario.id, f'{usuario.get_full_name()} ({usuario.email})') for usuario in Usuario.objects.all()]


class ProyectoCancelForm(forms.Form):
    nombre = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

# Crear un Rol de Proyecto


class RolProyectoForm(forms.Form):
    nombre = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    descripcion = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    permisos = forms.ModelMultipleChoiceField(queryset=None, widget=forms.CheckboxSelectMultiple())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['permisos'].queryset = PermisoProyecto.objects.all()

# Form para importar roles de otros proyectos


class ImportarRolProyectoForm(forms.Form):
    proyecto = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['proyecto'].choices = [(proyecto.id, proyecto.nombre) for proyecto in Proyecto.objects.all()]
