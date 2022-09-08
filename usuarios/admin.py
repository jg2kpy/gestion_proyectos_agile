from django.contrib import admin
from usuarios.models import RolSistema

from usuarios.models import Usuario, RolProyecto, PermisoProyecto

# Register your models here.
# ver el id del usuario en el admin
admin.site.register(Usuario)
admin.site.register(RolProyecto)
admin.site.register(PermisoProyecto)

# personalizar el admin y mostrar los campos que queremos
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'nombre', 'apellido', 'is_staff', 'is_active', 'is_superuser')
    list_filter = ('is_staff', 'is_active', 'is_superuser')
    search_fields = ('email', 'nombre', 'apellido')



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