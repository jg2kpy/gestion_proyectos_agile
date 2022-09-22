from django.contrib import admin
from historias_usuario.models import TipoHistoriaUsusario, HistoriaUsuario, EtapaHistoriaUsuario

# Register your models here.
class DefaultAdmin(admin.ModelAdmin):
   list_display = ('nombre', 'descripcion')

admin.site.register(TipoHistoriaUsusario, DefaultAdmin)
admin.site.register(HistoriaUsuario, DefaultAdmin)
admin.site.register(EtapaHistoriaUsuario, DefaultAdmin)