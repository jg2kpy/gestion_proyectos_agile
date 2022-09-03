from django.shortcuts import render
from .models import Proyecto
from .forms import ProyectoForm, ProyectoCancelForm, RolProyectoForm
from usuarios.models import Usuario , RolProyecto, PermisoProyecto
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

# Creamos una vista para ver los roles de proyectos
def roles_proyecto(request):
    return render(request, 'proyectos/roles_proyecto/roles_proyecto.html', {'roles_proyecto': RolProyecto.objects.all() ,'usuario' : request.user})

# Creamos un rol en un proyecto
def crear_rol_proyecto(request):
    if request.method == 'POST':
        form = RolProyectoForm(request.POST)
        if form.is_valid():
            # Creamos el rol
            rol = RolProyecto()
            rol.nombre = form.cleaned_data['nombre']
            rol.descripcion = form.cleaned_data['descripcion']
            rol.save()

            # Traemos todos los permisos de la base de datos
            permisos = PermisoProyecto.objects.all()

            # Traemos los permisos que se seleccionaron en el formulario
            permisos_seleccionados = form.cleaned_data['permisos']

            # Recorremos los permisos y los asignamos al rol
            for permiso in permisos:
                if permiso.nombre in permisos_seleccionados.values_list('nombre', flat=True):
                    #Agregamos el rol al permiso
                    permiso.rol.add(rol)
                    permiso.save()
                    

            return render(request, 'proyectos/roles_proyecto/roles_proyecto.html', {'roles_proyecto': RolProyecto.objects.all() ,'usuario' : request.user})
    else:
        form = RolProyectoForm()
    return render(request, 'proyectos/roles_proyecto/crear_rol_proyecto.html', {'form': form})

# Ver la informacion de un rol de un proyecto en especifico
def ver_rol_proyecto(request, id_rol_proyecto):
    rol = RolProyecto.objects.get(id=id_rol_proyecto)

    # Traemos los permisos del rol
    permisos = PermisoProyecto.objects.filter(rol=rol)

    return render(request, 'proyectos/roles_proyecto/ver_rol_proyecto.html', {'rol': rol, 'permisos': permisos})