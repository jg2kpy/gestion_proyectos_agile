from usuarios.models import PermisoProyecto
from django.core import management

if PermisoProyecto.objects.all().count() == 0:
    management.call_command('loaddata', 'databasedump.json')
