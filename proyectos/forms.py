from django import forms
from usuarios.models import Usuario
from .models import Proyecto
#Traemos los roles y los permisos de los proyectos
from usuarios.models import RolProyecto, PermisoProyecto



#Estados de proyecto
ESTADOS_PROYECTO = (
    ('Planificacion', 'Planificacion'),
    ('Ejecucion', 'Ejecucion'),
    ('Finalizado', 'Finalizado'),
    ('Cancelado', 'Cancelado'),
    ('En espera', 'En espera'),
)

#traemos los usuarios del sistema
USUARIOS = (
    (usuario.id, usuario.email) for usuario in Usuario.objects.all()
)

#Traemos los Permisos de los proyectos
PERMISOS = (
    (permiso.id, permiso.descripcion) for permiso in PermisoProyecto.objects.all()
)

PROYECTOS = (
    (proyecto.id, proyecto.nombre) for proyecto in Proyecto.objects.all()
)

class ProyectoForm(forms.Form):
    nombre = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    descripcion = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    fecha_inicio = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control'}))
    fecha_fin = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control'}))
    scrum_master = forms.ChoiceField(choices=USUARIOS, widget=forms.Select(attrs={'class': 'form-control'}))


class ProyectoCancelForm(forms.Form):
    nombre = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

#Crear un Rol de Proyecto
class RolProyectoForm(forms.Form):
    nombre = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    descripcion = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    permisos = forms.ModelMultipleChoiceField(queryset=PermisoProyecto.objects.all(), widget=forms.CheckboxSelectMultiple())

#Form para importar roles de otros proyectos
class ImportarRolProyectoForm(forms.Form):
    proyecto = forms.ChoiceField(choices= PROYECTOS,widget=forms.Select(attrs={'class': 'form-control'}))