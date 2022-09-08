from django import forms
from usuarios.models import Usuario
from .models import Proyecto
# Traemos los roles y los permisos de los proyectos
from usuarios.models import RolProyecto, PermisoProyecto

"""
    Enumerador de estados de Proyecto
    Indica los estados de proyecto que puede tener un proyecto
    y los estados que puede tener un proyecto en un momento dado.
"""
# Estados de proyecto
ESTADOS_PROYECTO = (
    ('Planificacion', 'Planificacion'),
    ('Ejecucion', 'Ejecucion'),
    ('Finalizado', 'Finalizado'),
    ('Cancelado', 'Cancelado'),
    ('En espera', 'En espera'),
)


class ProyectoForm(forms.Form):
    """
        Formulario para crear un proyecto
        Se introduce el nombre del proyecto, la descripcion, las fechas de inicio y de fin
        y se asigna un usuario como Scrum Master del proyecto

        :param nombre: Nombre del proyecto
        :type nombre: Texto
        :param descripcion: Descripcion del proyecto
        :type descripcion: Texto
        :param fecha_inicio: Fecha de inicio del proyecto
        :type fecha_inicio: Fecha
        :param fecha_fin: Fecha de fin del proyecto
        :type fecha_fin: Fecha
        :param scrum_master: Usuario que sera el Scrum Master del proyecto
        :type scrum_master: Usuario

        :return: Formulario para crear un proyecto
        :rtype: Proyecto
    """
    nombre = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    descripcion = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    scrum_master = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['scrum_master'].choices = [
            (usuario.id, f'{usuario.get_full_name()} ({usuario.email})') for usuario in Usuario.objects.all()]


class ProyectoCancelForm(forms.Form):
    """
        Formulario para cancelar un proyecto
        Se introduce el nombre del proyecto para confirmar que se desea cancelar el proyecto

        :param nombre: Nombre del proyecto
        :type nombre: Texto

        :return: Formulario para cancelar un proyecto
        :rtype: Formulario
    """
    nombre = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

# Crear un Rol de Proyecto
class RolProyectoForm(forms.Form):
    """
        Formulario para crear un rol de proyecto

        :param nombre: Nombre del rol de proyecto
        :type nombre: Texto
        :param descripcion: Descripcion del rol de proyecto
        :type descripcion: Texto
        :param permisos: Permisos del rol de proyecto
        :type permisos: Lista de permisos

        :return: Formulario para crear un rol de proyecto
        :rtype: Formulario
    """
    nombre = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    descripcion = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    permisos = forms.ModelMultipleChoiceField(queryset=None, widget=forms.CheckboxSelectMultiple())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['permisos'].queryset = PermisoProyecto.objects.all()

# Form para importar roles de otros proyectos

class ImportarRolProyectoForm(forms.Form):
    """
        Formulario para Seleccionar un proyecto para importar sus roles

        :param proyecto: Proyecto del cual se importaran los roles
        :type proyecto: Proyecto

        :return: Formulario para importar roles de proyecto
        :rtype: Formulario
    """
    proyecto = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['proyecto'].choices = [(proyecto.id, proyecto.nombre) for proyecto in Proyecto.objects.all()]
