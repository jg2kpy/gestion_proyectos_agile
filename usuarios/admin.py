from django.contrib import admin
from usuarios.models import RolSistema

# Register your models here.



# Temporal despues probablemente deba borrar
"""
Muestra Preview de los campos en admin
"""

class RolSistemaAdmin(admin.ModelAdmin):
   list_display = ('nombre', 'descripcion') 

"""
Registra el modelo en la vista de admin
"""
admin.site.register(RolSistema, RolSistemaAdmin)