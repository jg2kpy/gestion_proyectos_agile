from django import forms
from django.forms.utils import ErrorList

from historias_usuario.models import Comentario, EtapaHistoriaUsuario, HistoriaUsuario, SubirArchivo, TipoHistoriaUsusario

class DivErrorList(ErrorList):
    """ Lista de errores de un form estilizados
    """

    def __str__(self):
        """ Devuelve la lista de errores como un div html
        """
        return self.as_divs()

    def as_divs(self):
        """ Devuelve la lista de errores como un div html o un string vacío si no existen errores
        """
        if not self:
            return ''
        return """
                <div class="errorlist">
                    %s
                </div>
                """ % ''.join([
            """
                <div class="alert alert-danger alert-dismissible fade show" role="alert">
                    <h6>
                        %s
                    </h6>
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Cerrar">
                    </button>
                </div>
            """ % e for e in self])


class TipoHistoriaUsuarioForm(forms.ModelForm):
    """ Formulario para crear un tipo de historia de usuario
    """
    class Meta:
        """ Meta

        :param model: TipoHistoriaUsusario
        :type model: TipoHistoriaUsusario
        :param fields: ['nombre', 'descripcion']
        :type fields: list
        :param widgets: TextInput y TextClass con clase form-control
        :type widgets: dict
        """
        model = TipoHistoriaUsusario
        fields = ('nombre', 'descripcion')
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
        }


class EtapaHistoriaUsuarioForm(forms.ModelForm):
    """ Formulario para crear una etapa de historia de usuario
    """
    class Meta:
        """ Meta

        :param model: EtapaHistoriaUsuario
        :type model: EtapaHistoriaUsuario
        :param fields: ['nombre', 'descripcion']
        :type fields: list
        :param widgets: TextInput y TextClass con clase form-control
        :type widgets: dict
        """
        model = EtapaHistoriaUsuario
        fields = ('nombre', 'descripcion')
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'})
        }


class HistoriaUsuarioForm(forms.ModelForm):
    """ Formulario para crear una de historia de usuario
    """
    class Meta:
        """ Meta
        :param model: HistoriaUsusario
        :type model: HistoriaUsusario
        :param fields: [nombre', 'descripcion', 'bv', 'up', 'tipo', 'usuarioAsignado']
        :type fields: list
        :param widgets: TextInput, Textarea, NumberInput, forms.Select con clase form-control
        :type widgets: dict
        :param labels: nombre, descripcion, bv, up, tipo, usuarioAsignado
        :type widgets: dict
        """
        model = HistoriaUsuario
        fields = ('nombre', 'descripcion', 'bv',
                  'up', 'tipo', 'usuarioAsignado')
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'bv': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'up': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'usuarioAsignado': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            "nombre": "Nombre",
            "descripcion": "Descripción",
            "bv": "Business Value (Prioridad de negocio)",
            "up": "User Point (Prioridad técnica)",
            "tipo": "Tipo de Historia de Usuario",
            "usuarioAsignado": "Usuario asignado"
        }
    
    def __init__(self, *args, **kwargs):
        super(HistoriaUsuarioForm, self).__init__(*args, **kwargs)
        self.fields['usuarioAsignado'].required = False
        self.fields['up'].required = False
    
    def set_tipos_usuarios(self, tipos, usuarios):
        self.fields['tipo'].choices = tipos
        self.fields['usuarioAsignado'].choices = usuarios
        

class HistoriaUsuarioProductOwnerForm(forms.ModelForm):
    """ Formulario para crear una de historia de usuario siendo un product owner
    """
    class Meta:
        """ Meta
        :param model: HistoriaUsusario
        :type model: HistoriaUsusario
        :param fields: [nombre', 'descripcion', 'bv', 'tipo']
        :type fields: list
        :param widgets: TextInput, Textarea, NumberInput, forms.Select con clase form-control
        :type widgets: dict
        :param labels: nombre, descripcion, up, tipo
        :type widgets: dict
        """
        model = HistoriaUsuario
        fields = ('nombre', 'descripcion', 'bv', 'tipo')
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'bv': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            "nombre": "Nombre",
            "descripcion": "Descripción",
            "bv": "Business Value (Prioridad de negocio)",
            "tipo": "Tipo de Historia de Usuario"
        }
    
    def set_tipos(self, tipos):
        self.fields['tipo'].choices = tipos


class HistoriaUsuarioEditarForm(forms.ModelForm):
    """ Formulario para editar una de historia de usuario
    """
    class Meta:
        """ Meta

        :param model: HistoriaUsusario
        :type model: HistoriaUsusario
        :param fields: [nombre', 'descripcion', 'bv', 'up', 'usuarioAsignado']
        :type fields: list
        :param widgets: TextInput, Textarea, NumberInput, forms.Select con clase form-control
        :type widgets: dict
        :param labels: nombre, descripcion, bv, up, usuarioAsignado
        :type widgets: dict
        """
        model = HistoriaUsuario
        fields = ('descripcion', 'bv', 'up', 'usuarioAsignado')
        widgets = {
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'bv': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'up': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'usuarioAsignado': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            "descripcion": "Descripción",
            "bv": "Business Value (Prioridad de negocio)",
            "up": "User Point (Prioridad técnica)",
            "usuarioAsignado": "Usuario asignado"
        }
    
    def set_usuarios(self, usuarios):
        self.fields['usuarioAsignado'].choices = usuarios


class ComentarioForm(forms.ModelForm):
    """ Formulario para crear un comentario
    """
    class Meta:
        """ Meta

        :param model: Comentario
        :type model: Comentario
        :param fields: ['contenido']
        :type fields: list
        :param widgets: TextArea
        :type widgets: dict
        """
        model = Comentario
        fields = ('contenido',)
        widgets = {
            'contenido': forms.Textarea(attrs={'class': 'form-control'})
        }
        labels = {
            "contenido": "Comentario"
        }

class SubirArchivoForm(forms.ModelForm):
    """
    Formulario para subir un archivo
    """
    class Meta:
        """ Meta
        :param model: SubirArchivo
        :type model: SubirArchivo
        :param fields: ['archivo']
        :type fields: list
        :param widgets: ClearableFileInput
        :type widgets: dict
        :param labels: archivo
        :type widgets: dict
        """
        model = SubirArchivo
        fields = ('archivo',)
        widgets = {
            'archivo': forms.ClearableFileInput(attrs={'multiple': True}),
        }
        labels = {
            'archivo': 'Archivo'
        }