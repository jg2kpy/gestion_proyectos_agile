from django.contrib import admin
from .models import ArchivoBurndown, Feriado, Proyecto
from proyectos.models import Sprint

# Register your models here.
admin.site.register(Proyecto)
admin.site.register(Sprint)
admin.site.register(Feriado)
admin.site.register(ArchivoBurndown)
