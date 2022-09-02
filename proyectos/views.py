from django.shortcuts import render
from .models import Proyecto
from .forms import ProyectoForm
from usuarios.models import Usuario

#Creamos una vista para ver los proyectos
def proyectos(request):
    return render(request, 'proyectos/base.html', {'proyectos': Proyecto.objects.all()})


# Recibimos una peticion POST para crear un proyecto
def crear_proyecto(request):
    if request.method == 'POST':
        form = ProyectoForm(request.POST)
        if form.is_valid():
            # Creamos el proyecto
            proyecto = Proyecto()
            proyecto.nombre = form.cleaned_data['nombre']
            proyecto.descripcion = form.cleaned_data['descripcion']
            proyecto.fecha_inicio = form.cleaned_data['fecha_inicio']
            proyecto.fecha_fin = form.cleaned_data['fecha_fin']
            proyecto.estado = form.cleaned_data['estado']
            id_scrum_master = form.cleaned_data['scrum_master']
            scrum_master = Usuario.objects.get(id=id_scrum_master)
            proyecto.scrumMaster = scrum_master
            proyecto.save()
            return render(request, 'proyectos/base.html', {'proyectos': Proyecto.objects.all()})
    else:
        form = ProyectoForm()
    return render(request, 'proyectos/crear_proyecto.html', {'form': form})