from django.shortcuts import render
from .models import Proyecto
from .forms import ProyectoForm
from .forms import ProyectoCancelForm
from usuarios.models import Usuario
from gestion_proyectos_agile.templatetags.tiene_rol_en import tiene_rol_en_proyecto
from gestion_proyectos_agile.templatetags.tiene_rol_en import tiene_rol_en_sistema

#Estados de Proyecto
ESTADOS_PROYECTO = (
    ('Planificacion', 'Planificacion'),
    ('Ejecucion', 'Ejecucion'),
    ('Finalizado', 'Finalizado'),
    ('Cancelado', 'Cancelado'),
    ('En espera', 'En espera'),
)



#Creamos una vista para ver los proyectos
def proyectos(request):
    return render(request, 'proyectos/base.html', {'proyectos': Proyecto.objects.all() ,'usuario' : request.user})



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
            proyecto.estado = ESTADOS_PROYECTO.__getitem__(0)[0] #Automaticamente el estado se queda en planificado
            id_scrum_master = form.cleaned_data['scrum_master']
            scrum_master = Usuario.objects.get(id=id_scrum_master)
            proyecto.scrumMaster = scrum_master
            proyecto.save()
            return render(request, 'proyectos/base.html', {'proyectos': Proyecto.objects.all()})
    else:
        form = ProyectoForm()
    return render(request, 'proyectos/crear_proyecto.html', {'form': form})

# Recibimos una peticion POST para cancelar un proyecto
def cancelar_proyecto(request, id_proyecto):
    # Verificamos que el usuario tenga permisos rol de moderador o es el scrum master del proyecto
    if request.method == 'POST':
        form = ProyectoCancelForm(request.POST)
        if form.is_valid():
            # Cancelamos el proyecto
            #verificamos que el nombre del proyecto sea correcto
            if form.cleaned_data['nombre'] == Proyecto.objects.get(id=id_proyecto).nombre:
                proyecto = Proyecto.objects.get(id=id_proyecto)
                proyecto.estado = 'Cancelado'
                proyecto.save()
                return render(request, 'proyectos/base.html', {'proyectos': Proyecto.objects.all()})
            else: 
                print('El nombre del proyecto no es correcto')
                return render(request, 'proyectos/base.html', {'proyectos': Proyecto.objects.all()})
    else:
        form = ProyectoCancelForm()
    return render(request, 'proyectos/cancelar_proyecto.html', {'form': form})