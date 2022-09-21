from django import forms
from historias_usuario.models import EtapaHistoriaUsuario, HistoriaUsuario, TipoHistoriaUsusario
from django.forms.utils import ErrorList


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
        model = HistoriaUsuario
        fields = ('nombre', 'descripcion', 'bv', 'tipo', 'usuarioAsignado')
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'bv': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'usuarioAsignado': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            "nombre": "Nombre",
            "descripcion": "Descripcion",
            "bv": "Business Value",
            "tipo": "Tipo de Historia de Usuario",
            "usuarioAsignado": "Usuario asignado"
        }
