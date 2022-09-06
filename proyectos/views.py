from django.shortcuts import render
from .models import Proyecto
from .forms import ProyectoForm, ProyectoCancelForm, RolProyectoForm, ImportarRolProyectoForm
from usuarios.models import Usuario, RolProyecto, PermisoProyecto
from django.views.decorators.cache import never_cache

# Estados de Proyecto
ESTADOS_PROYECTO = (
    ('Planificacion', 'Planificacion'),
    ('Ejecucion', 'Ejecucion'),
    ('Finalizado', 'Finalizado'),
    ('Cancelado', 'Cancelado'),
    ('En espera', 'En espera'),
)


# Creamos una vista para ver los proyectos
def proyectos(request):
    return render(request, 'proyectos/base.html', {'proyectos': Proyecto.objects.all(), 'usuario': request.user})


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
            proyecto.estado = ESTADOS_PROYECTO.__getitem__(0)[0]  # Automaticamente el estado se queda en planificado
            id_scrum_master = form.cleaned_data['scrum_master']
            scrum_master = Usuario.objects.get(id=id_scrum_master)
            proyecto.scrumMaster = scrum_master
            proyecto.save()

            scrum_master.equipo.add(proyecto)

            # Traemos el ID del proyecto recien creado
            # Traemos todos los roles que tenga null como proyecto_id
            roles = RolProyecto.objects.filter(proyecto__isnull=True)
            # Generamos una copia de este rol y el asignamos el id del proyecto
            for rol in roles:
                # Creamos el rol
                rol_nuevo = RolProyecto()
                rol_nuevo.nombre = rol.nombre
                rol_nuevo.descripcion = rol.descripcion
                rol_nuevo.proyecto = Proyecto.objects.get(id=proyecto.id)
                rol_nuevo.save()

                # Traemos los permisos del rol
                permisos = PermisoProyecto.objects.filter(rol=rol)

                # Recorremos los permisos y los asignamos al rol
                for permiso in permisos:
                    # Agregamos el rol al permiso
                    permiso.rol.add(rol_nuevo)
                    permiso.save()

            scrum_master.roles_proyecto.add(RolProyecto.objects.get(nombre="Scrum Master", proyecto=proyecto))
            scrum_master.save()

            return render(request, 'proyectos/base.html', {'proyectos': Proyecto.objects.all()})
    else:
        form = ProyectoForm()
    return render(request, 'proyectos/crear_proyecto.html', {'form': form})

#Editar un proyecto
def editar_proyecto(request, id_proyecto):
    # Verificamos que el usuario tenga permisos rol de moderador o es el scrum master del proyecto
    if request.method == 'POST':
        form = ProyectoForm(request.POST)
        if form.is_valid():
            # Editamos el proyecto
            proyecto = Proyecto.objects.get(id=id_proyecto)
            proyecto.nombre = form.cleaned_data['nombre']
            proyecto.descripcion = form.cleaned_data['descripcion']
            proyecto.fecha_inicio = form.cleaned_data['fecha_inicio']
            proyecto.fecha_fin = form.cleaned_data['fecha_fin']
            proyecto.save()
            return render(request, 'proyectos/base.html', {'proyectos': Proyecto.objects.all()})
    else:
        form = ProyectoForm()
        # cargamos los datos del proyecto
        proyecto = Proyecto.objects.get(id=id_proyecto)
        form.fields['nombre'].initial = proyecto.nombre
        form.fields['descripcion'].initial = proyecto.descripcion
        #TODO Fix de las fechas de inicio y fin
        form.fields['fecha_inicio'].initial = proyecto.fecha_creacion
        form.fields['fecha_fin'].initial = proyecto.fecha_modificacion


    return render(request, 'proyectos/editar_proyecto.html', {'form': form})

# Recibimos una peticion POST para cancelar un proyecto
def cancelar_proyecto(request, id_proyecto):
    # Verificamos que el usuario tenga permisos rol de moderador o es el scrum master del proyecto
    if request.method == 'POST':
        form = ProyectoCancelForm(request.POST)
        if form.is_valid():
            # Cancelamos el proyecto
            # verificamos que el nombre del proyecto sea correcto
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

    # Si el proyecto ya esta cancelado no se puede cancelar de nuevo
    if Proyecto.objects.get(id=id_proyecto).estado == ESTADOS_PROYECTO.__getitem__(3)[0]:
        return render(request, 'proyectos/base.html', {'proyectos': Proyecto.objects.all()})

    return render(request, 'proyectos/cancelar_proyecto.html', {'form': form})

# Creamos una vista para ver los roles de proyectos


def roles_proyecto(request):
    return render(request, 'proyectos/roles_proyecto/roles_proyecto.html', {'roles_proyecto': RolProyecto.objects.all(), 'usuario': request.user})

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
                    # Agregamos el rol al permiso
                    permiso.rol.add(rol)
                    permiso.save()

            return render(request, 'proyectos/roles_proyecto/roles_proyecto.html', {'roles_proyecto': RolProyecto.objects.all(), 'usuario': request.user})
    else:
        form = RolProyectoForm()
    return render(request, 'proyectos/roles_proyecto/crear_rol_proyecto.html', {'form': form})

# Ver la informacion de un rol de un proyecto en especifico


def ver_rol_proyecto(request, id_rol_proyecto):
    rol = RolProyecto.objects.get(id=id_rol_proyecto)

    # Traemos los permisos del rol
    permisos = PermisoProyecto.objects.filter(rol=rol)

    return render(request, 'proyectos/roles_proyecto/ver_rol_proyecto.html', {'rol': rol, 'permisos': permisos})

# Modificar un rol de un proyecto


def modificar_rol_proyecto(request, id_rol_proyecto):
    rol = RolProyecto.objects.get(id=id_rol_proyecto)

    # Traemos los permisos del rol
    permisos = PermisoProyecto.objects.filter(rol=rol)

    if request.method == 'POST':
        form = RolProyectoForm(request.POST)
        if form.is_valid():
            # Modificamos el rol
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
                    # Agregamos el rol al permiso
                    permiso.rol.add(rol)
                    permiso.save()
                else:
                    # Eliminamos el rol del permiso
                    permiso.rol.remove(rol)
                    permiso.save()

            return render(request, 'proyectos/roles_proyecto/roles_proyecto.html', {'roles_proyecto': RolProyecto.objects.all(), 'usuario': request.user})
    else:
        form = RolProyectoForm(initial={'nombre': rol.nombre, 'descripcion': rol.descripcion})
    return render(request, 'proyectos/roles_proyecto/modificar_rol_proyecto.html', {'form': form, 'rol': rol, 'permisos': permisos})

# Eliminar un rol de un proyecto


def eliminar_rol_proyecto(request, id_rol_proyecto):
    if request.method == 'POST':
        rol = RolProyecto.objects.get(id=id_rol_proyecto)
        rol.delete()
        return render(request, 'proyectos/roles_proyecto/roles_proyecto.html', {'roles_proyecto': RolProyecto.objects.all(), 'usuario': request.user})
    return render(request, 'proyectos/roles_proyecto/eliminar_rol_proyecto.html', {'rol_proyecto': RolProyecto.objects.get(id=id_rol_proyecto)})

# Ver roles asignados a un proyecto


def ver_roles_asignados(request, id_proyecto):
    # Traemos los roles que tengan el id del proyecto
    roles = RolProyecto.objects.filter(proyecto=id_proyecto)

    return render(request, 'proyectos/roles_proyecto/roles_proyecto.html', {'roles_proyecto': roles, 'id_proyecto': id_proyecto})

# Creamos un rol en un proyecto a un proyecto especifico


def crear_rol_a_proyecto(request, id_proyecto):
    if request.method == 'POST':
        form = RolProyectoForm(request.POST)
        if form.is_valid():
            # Creamos el rol
            rol = RolProyecto()
            rol.nombre = form.cleaned_data['nombre']
            rol.descripcion = form.cleaned_data['descripcion']
            rol.proyecto = Proyecto.objects.get(id=id_proyecto)
            rol.save()

            # Traemos todos los permisos de la base de datos
            permisos = PermisoProyecto.objects.all()

            # Traemos los permisos que se seleccionaron en el formulario
            permisos_seleccionados = form.cleaned_data['permisos']

            # Recorremos los permisos y los asignamos al rol
            for permiso in permisos:
                if permiso.nombre in permisos_seleccionados.values_list('nombre', flat=True):
                    # Agregamos el rol al permiso
                    permiso.rol.add(rol)
                    permiso.save()

            return render(request, 'proyectos/roles_proyecto/roles_proyecto.html', {'roles_proyecto': RolProyecto.objects.filter(proyecto=id_proyecto)})
    else:
        form = RolProyectoForm()
    return render(request, 'proyectos/roles_proyecto/crear_rol_proyecto.html', {'form': form, 'id_proyecto': id_proyecto})

# Importar Rol de otros proyectos

@never_cache
def importar_rol(request, id_proyecto):
    if request.method == 'POST':
        # id_proyecto: Proyecto a donde se VA A IMPORTAR
        roles = [] # Lista de los id de los roles a importar
        proyecto_seleccionado = Proyecto.objects.get(id=int(request.POST.get('proyecto_seleccionado'))) # Proyecto de donde SE IMPORTA los roles
        for rol in proyecto_seleccionado.proyecto_rol.all():
            if request.POST.get(f'{rol.id}') != None:
                roles.append(rol)

        # Recorremos los roles y creamos nuevos roles con los mismos permisos
        for rol in roles:
            if rol.nombre not in RolProyecto.objects.filter(proyecto=id_proyecto).values_list('nombre', flat=True):
                # Creamos el rol
                rol_nuevo = RolProyecto()
                rol_nuevo.nombre = rol.nombre
                rol_nuevo.descripcion = rol.descripcion
                rol_nuevo.proyecto = Proyecto.objects.get(id=id_proyecto)
                rol_nuevo.save()

                # Traemos los permisos del rol
                permisos = PermisoProyecto.objects.filter(rol=rol)

                # Recorremos los permisos y los asignamos al rol
                for permiso in permisos:
                    # Agregamos el rol al permiso
                    permiso.rol.add(rol_nuevo)
                    permiso.save()

        return render(request, 'proyectos/roles_proyecto/roles_proyecto.html', {'roles_proyecto': RolProyecto.objects.filter(proyecto=id_proyecto)})

    else:
        proyectos = Proyecto.objects.exclude(id=id_proyecto)
        # proyecto_objetivo = Proyecto.objects.get(nombre = request.GET.get('proyectos'))
        if request.GET.get('proyectos'): # Este es el GET cuando solicita ver los roles de proyectos de un proyecto en especifico
            proyecto = Proyecto.objects.get(nombre = request.GET.get('proyectos'))
            roles = RolProyecto.objects.filter(proyecto = proyecto)
        else:# Este es el GET cuando se llama desde otra pagina
            proyecto = proyectos[0]
            roles = RolProyecto.objects.filter(proyecto = proyectos[0])
        
    return render(request, 'proyectos/roles_proyecto/importar_rol.html', {'proyectos': proyectos, 'proyecto_seleccionado': proyecto, 'roles': roles})
