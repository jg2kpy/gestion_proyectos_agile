from django import forms
from pkg_resources import require
from usuarios.models import Usuario
from .models import Feriado, Proyecto
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


class ProyectoForm(forms.ModelForm):
    """
        Formulario para crear un proyecto
        Se introduce el nombre del proyecto, la descripcion, las fechas de inicio y de fin
        y se asigna un usuario como Scrum Master del proyecto

        :param nombre: Nombre del proyecto
        :type nombre: Texto
        :param descripcion: Descripcion del proyecto
        :type descripcion: Texto
        :param scrum_master: Usuario que sera el Scrum Master del proyecto
        :type scrum_master: Usuario
        :param minimo_dias_sprint: Minimo de dias para un sprint de este proyecto
        :type minimo_dias_sprint: int
        :param maximo_dias_sprint: Maximo de dias para un sprint de este proyecto
        :type maximo_dias_sprint: int

        :return: Formulario para crear un proyecto
        :rtype: Form
    """
    class Meta:

        model = Proyecto
        fields = ('nombre', 'descripcion','scrumMaster','minimo_dias_sprint','maximo_dias_sprint')
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'scrumMaster': forms.Select(attrs={'class': 'form-control'}),
            'minimo_dias_sprint': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'maximo_dias_sprint': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'})
        }
        initial={
            'minimo_dias_sprint': 15,
            'maximo_dias_sprint': 30,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['scrumMaster'].choices = [
            (usuario.id, f'{usuario.get_full_name()} ({usuario.email})') for usuario in Usuario.objects.all()]
        self.fields['minimo_dias_sprint'].required = False
        self.fields['maximo_dias_sprint'].required = False


class ProyectoConfigurarForm(forms.ModelForm):
    """
        Formulario para configurar un proyecto
        Se introduce el nombre del proyecto, la descripcion, las fechas de inicio y de fin
        y se asigna un usuario como Scrum Master del proyecto

        :param descripcion: Descripcion del proyecto
        :type descripcion: Texto
        :param scrum_master: Usuario que sera el Scrum Master del proyecto
        :type scrum_master: Usuario
        :param minimo_dias_sprint: Minimo de dias para un sprint de este proyecto
        :type minimo_dias_sprint: int
        :param maximo_dias_sprint: Maximo de dias para un sprint de este proyecto
        :type maximo_dias_sprint: int

        :return: Formulario para crear un proyecto
        :rtype: Form
    """

    class Meta:
        model = Proyecto
        fields = ('descripcion', 'minimo_dias_sprint', 'maximo_dias_sprint')
        widgets = {
            # 'nombre': forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'minimo_dias_sprint': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'maximo_dias_sprint': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['minimo_dias_sprint'].required = False
        self.fields['maximo_dias_sprint'].required = False


class ProyectoFeriadosForm(forms.ModelForm):
    """
        Formulario para agregar feriados a un proyecto
        Se introduce los feriados que se desean agregar al proyecto

        :param descripcion: Descripcion del feriado
        :type descripcion: str
        :param fecha: FEcha del feriado
        :type fecha: Date

        :return: Formulario para agregar feriados
        :rtype: Form
    """

    class Meta:
        model = Feriado
        fields = ('descripcion', 'fecha')
        widgets = {
            'descripcion': forms.TextInput(attrs={'class': 'form-control', 'required': 'requiered'}),
            'fecha': forms.DateInput(format='%Y-%m-%d', attrs={'type':'date', 'class': 'form-control', 'required': 'requiered'})
        }
        required={
            'descripcion': False,
            'fecha': False,
        }

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
