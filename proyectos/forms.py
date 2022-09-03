from django import forms
from usuarios.models import Usuario

#Importamos el modelo de usuarios

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
    (usuario.id, usuario.username) for usuario in Usuario.objects.all()
)


class ProyectoForm(forms.Form):
    nombre = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    descripcion = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    fecha_inicio = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control'}))
    fecha_fin = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control'}))
    scrum_master = forms.ChoiceField(choices=USUARIOS, widget=forms.Select(attrs={'class': 'form-control'}))

# puede ser null el nombre
class ProyectoCancelForm(forms.Form):
    nombre = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

