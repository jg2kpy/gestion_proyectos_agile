from django.contrib import admin
from .models import Proyecto
from proyectos.models import Sprint

# Register your models here.
admin.site.register(Proyecto)
admin.site.register(Sprint)
