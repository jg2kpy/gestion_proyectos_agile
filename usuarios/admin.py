from django.contrib import admin

from usuarios.models import Usuario

# Register your models here.
# ver el id del usuario en el admin
admin.site.register(Usuario)

# personalizar el admin y mostrar los campos que queremos
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'nombre', 'apellido', 'is_staff', 'is_active', 'is_superuser')
    list_filter = ('is_staff', 'is_active', 'is_superuser')
    search_fields = ('email', 'nombre', 'apellido')

