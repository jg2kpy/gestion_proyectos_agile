from django import forms
from historias_usuario.models import EtapaHistoriaUsuario, TipoHistoriaUsusario
from django.forms.utils import ErrorList


class DivErrorList(ErrorList):
    def __str__(self):
        return self.as_divs()

    def as_divs(self):
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
    class Meta:
        model = TipoHistoriaUsusario
        fields = ('nombre', 'descripcion')
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
        }


class EtapaHistoriaUsuarioForm(forms.ModelForm):
    class Meta:
        model = EtapaHistoriaUsuario
        fields = ('nombre', 'descripcion')
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'})
        }
