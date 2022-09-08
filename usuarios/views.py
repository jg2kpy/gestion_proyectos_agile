from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.forms import ModelForm
from django.views.decorators.cache import never_cache

from gestion_proyectos_agile.templatetags.tiene_rol_en import tiene_rol_en_proyecto
from proyectos.models import Proyecto
from usuarios.models import RolProyecto, Usuario
from .models import Usuario

from usuarios.models import RolSistema, Usuario
from django import forms
from django.shortcuts import redirect

# Crea forms
class RolSistemaForm(forms.ModelForm):
    """
    Model form para los Roles de Globales con los campos nombre y descripcion
    En la funcion clean se realizan las validaciones por parte del servidor
    """
    class Meta:
        model = RolSistema
        fields = ['nombre', 'descripcion']
    
    def clean(self):
        super(RolSistemaForm, self).clean()
         
        nombre = self.cleaned_data.get('nombre')
        descripcion = self.cleaned_data.get('descricpion')
 
        if not nombre:
            self._errors['nombre'] = self.error_class([
                'No puede quedar vacio el campo'])
        if nombre and len(nombre) < 3:
            self._errors['nombre'] = self.error_class([
                'Debe tener más de 2 caracteres'])
        if nombre and len(nombre) > 255:
            self._errors['nombre'] = self.error_class([
                'El máximo de caracteres permitidos es 255'])
        if descripcion and len(descripcion) > 500:
            self._errors['descripcion'] = self.error_class([
                'El máximo de caracteres permitidos es 500'])
 
        return self.cleaned_data


@never_cache
def rol_global_list(request):
    """
    Vista para el menu de roles globales, funcion que maneja el endpoint /rolesglobales/
    Contiene función para eliminar rol global por medio de ventana popup

    :param request: Solicitud HTTP del cliente junto con el body con los datos para la realizar la operacion solicitada
    :type request: HttpRequest

    :return: Se retorna una respuesta HttpResponse que puede ser un 401 en caso de no tener la autorizacion, 200 en caso de
        cargar correctamente el contenido o redirecciona a la página referente a la lista de roles globales
    :rtype: HttpResponse
    """
    status = 200

    if not request.user.is_authenticated:
        return HttpResponseRedirect('Usuario no autenticado', status=401)
    
    if request.POST.get('accion') == 'eliminar':
        rol = RolSistema.objects.get(nombre=request.POST.get('nombre'))
        rol.delete()
        return redirect('rol_global_list')

    else:
        roles = RolSistema.objects.all()
        return render(request, 'rol_global/rol_global_list.html', {'roles': roles}, status=status)

@never_cache
def rol_global_crear(request):
    """
    Vista para creacion y guardado en la base de datos de un rol global

    :param request: Solicitud HTTP del cliente junto con el body con los datos para la realizar la operacion solicitada
    :type request: HttpRequest

    :return: Se retorna una respuesta HttpResponse que muestra la página actualizada con código 200 en caso exitoso,
        401 si no se encuentra logueado o 422 si el formulario no fue llenado correctamente o redirecciona a la página
        referente a la lista de roles globales
    :rtype: HttpResponse
    """
    status = 200

    if not request.user.is_authenticated:
        return HttpResponseRedirect('Usuario no autenticado', status=401)
    
    if request.method == 'POST':
        form = RolSistemaForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('rol_global_list')

        else:
            status = 422

    else:
        form = RolSistemaForm()

    return render(request, 'rol_global/rol_global_crear.html', {'form': form}, status=status)

@never_cache
def rol_global_editar(request, id):
    """
    Vista para edicion de los atributos de un rol global

    :param request: Solicitud HTTP del cliente junto con el body con los datos para la realizar la operacion solicitada
    :type request: HttpRequest

    :param id: Id del proyecto que se recibe por URL
    :type id: int

    :return: Se retorna una respuesta HttpResponse que muestra la página actualizada con código 200 en caso exitoso,
        401 si no se encuentra logueado o 422 si el formulario no fue llenado correctamente o redirecciona a la página
        referente a la lista de roles globales
    :rtype: HttpResponse
    """
    status = 200

    if not request.user.is_authenticated:
        return HttpResponseRedirect('Usuario no autenticado', status=401)
        
    rol = RolSistema.objects.get(id=id)
    
    if request.method == 'POST':
        form = RolSistemaForm(request.POST, instance=rol)
    
        if form.is_valid():
            form.save()
            return redirect('rol_global_list')

        else:
            status = 422
    else:
        form = RolSistemaForm(instance=rol)

    return render(request, 'rol_global/rol_global_editar.html', {'form': form, 'rol':rol}, status=status)

@never_cache
def rol_global_usuarios(request, id):
    """
    Vista para la vinculacion y desvinculacion de roles globales a un usuario junto con las restricciones necesarias

    :param request: Solicitud HTTP del cliente junto con el body con los datos para la realizar la operacion solicitada
    :type request: HttpRequest

    :param id: Id del proyecto que se recibe por URL
    :type id: int

    :return: Se retorna una respuesta HttpResponse que muestra la página actualizada con código 200 en caso exitoso,
        401 si no se encuentra logueado, 422 en caso de no seleccionar un usuario e intentar realizar una operacion
    :rtype: HttpResponse
    """
    status = 200

    if not request.user.is_authenticated:
        return HttpResponseRedirect('Usuario no autenticado', status=401)

    rol = RolSistema.objects.get(id=id)

    if request.method == 'POST':
        email = request.POST.get('usuarios')

        if not email:
            estado = 'vacio'
            status = 422
            return render(request, 'rol_global/rol_global_validacion.html', {'estado': estado, 'rol': rol}, status=status)
        
        usuario = Usuario.objects.get(email=email)
        
        if 'vincular' in request.POST:
            if usuario.roles_sistema.filter(id=id).exists():
                estado = 'posee_rol'
                
            else:
                usuario.roles_sistema.add(rol)
                estado = 'vinculado'
            
        else:
            if usuario.roles_sistema.filter(id=id).exists():
                usuario.roles_sistema.remove(rol)
                estado = 'desvinculado'
                
            else:
                estado = 'rol_inexistente'
            
        return render(request, 'rol_global/rol_global_validacion.html', {'estado': estado, 'usuario': usuario, 'rol': rol}, status=status)

    else:
        usuarios = Usuario.objects.all()
        return render(request, 'rol_global/rol_global_usuarios.html', {'id': id, 'usuarios': usuarios, 'rol': rol}, status=status)


@never_cache
def vista_equipo(request, proyecto_id):
    """Vista de equipo, funcion que maneja el endpoint /usuarios/equipo/<proyecto_id>

    :param request: Solicitud HTTP del cliente junto con el body con los datos para la realizar la operacion solicitada
    :type request: HttpRequest

    :param proyecto_id: Id del proyecto que se recibe por URL
    :type proyecto_id: int

    :return: Se retorna una respuesta HttpResponse que puede ser un 401 (no autorizado), 404 (proyecto no existe) o 403 (no tiene permiso de ver este proyecto), en caso de ser una peticion GET, se retorna el HTML correspondiente o en POST se realiza la accion solicitada
    :rtype: HttpResponse
    """
    if not request.user.is_authenticated:
        return HttpResponse('Usuario no autenticado', status=401)

    if Proyecto.objects.filter(id=proyecto_id).count() == 0:
        return HttpResponse('Proyecto no existe', status=404)

    if not request.user.equipo.filter(id=proyecto_id):
        return HttpResponse('Usuario no pertenece al proyecto', status=403)

    if request.method == 'POST':
        form = request.POST
        hidden_action = form.get('hidden_action')

        if hidden_action == 'eliminar_miembro_proyecto':
            return eliminar_miembro_proyecto(form, request.user, proyecto_id)
        elif hidden_action == 'agregar_miembro_proyecto':
            return agregar_miembro_proyecto(request, form, request.user, proyecto_id)
        elif hidden_action == 'eliminar_rol_proyecto':
            return eliminar_rol_proyecto(form, request.user, proyecto_id)
        elif hidden_action == 'asignar_rol_proyecto':
            return asignar_rol_proyecto(form, request.user, proyecto_id)

    return render(request, 'usuarios_equipos/equiporoles.html', {'proyecto_id': proyecto_id})


def eliminar_miembro_proyecto(form, request_user, proyecto_id):
    """Eliminar miembros de un proyecto, endpoint /usuarios/equipo/<proyecto_id>

    :param form: Un objeto similar a un diccionario que contiene todos los parámetros HTTP POST dados.
    :type form: QueryDict

    :param request_user: Objeto de tipo Usuario del cual se realizo la peticion HTTP
    :type request_user: Usuario

    :param proyecto_id: Id del proyecto que se recibe por URL
    :type proyecto_id: int

    :return: Se retorna una respuesta HttpResponse que puede ser un 403 en caso de no tener la autorizacion, 422 en caso que el formulario tenga datos erroneos o retornar a la pagina principal
    :rtype: HttpResponse
    """

    if not tiene_rol_en_proyecto(request_user, "Scrum Master", proyecto_id):
        return HttpResponse('Usuario no posee el permiso de realizar esta accion', status=403)

    try:
        usuario_email = form.get('usuario_a_eliminar')
        usuario_a_eliminar_miembro_proyecto = Usuario.objects.get(email=usuario_email)
        proyecto = Proyecto.objects.get(id=proyecto_id)
        roles = RolProyecto.objects.filter(usuario=usuario_a_eliminar_miembro_proyecto, proyecto=proyecto_id)
        [usuario_a_eliminar_miembro_proyecto.roles_proyecto.remove(r) for r in roles]
        usuario_a_eliminar_miembro_proyecto.equipo.remove(proyecto)

    except Usuario.DoesNotExist:
        return HttpResponse('Usuario no existe', status=422)

    return redirect(f'/usuarios/equipo/{proyecto_id}')


def agregar_miembro_proyecto(request, form, request_user, proyecto_id):
    """Agregar miembro al proyecto, endpoint /usuarios/equipo/<proyecto_id>

    :param request: Solicitud HTTP del cliente junto con el body con los datos del nombre de usuario  e id del rol
    :type request: HttpRequest

    :param form: Un objeto similar a un diccionario que contiene todos los parámetros HTTP POST dados.
    :type form: QueryDict

    :param request_user: Objeto de tipo Usuario del cual se realizo la peticion HTTP
    :type request_user: Usuario

    :param proyecto_id: Id del proyecto que se recibe por URL
    :type proyecto_id: int

    :return: Se retorna una respuesta HttpResponse que puede ser un 403 en caso de no tener la autorizacion, 422 en caso que el formulario tenga datos erroneos o retornar a la pagina principal
    :rtype: HttpResponse
    """

    if not tiene_rol_en_proyecto(request_user, "Scrum Master", proyecto_id):
        return HttpResponse('Usuario no posee el permiso de realizar esta accion', status=403)

    try:
        usuario_email = form.get('usuario_a_agregar')
        rol_id = form.get('roles_agregar')
        usuario_a_agregar_miembro_proyecto = Usuario.objects.get(email=usuario_email)
        proyecto = Proyecto.objects.get(id=proyecto_id)

        if usuario_a_agregar_miembro_proyecto.equipo.filter(id=proyecto.id).count() != 0:
            return render(request, 'usuarios_equipos/equiporoles.html', {'mensaje': 'El usuario ya pertenece al proyecto', 'proyecto_id': proyecto_id}, status=422)

        usuario_a_agregar_miembro_proyecto.equipo.add(proyecto)
        rol_proyecto = RolProyecto.objects.get(id=rol_id)
        usuario_a_agregar_miembro_proyecto.roles_proyecto.add(rol_proyecto)

    except Usuario.DoesNotExist:
        return render(request, 'usuarios_equipos/equiporoles.html', {'mensaje': 'El usuario no existe', 'proyecto_id': proyecto_id}, status=422)

    return redirect(f'/usuarios/equipo/{proyecto_id}')


def eliminar_rol_proyecto(form, request_user, proyecto_id):
    """Eliminar miembros de un proyecto, endpoint /usuarios/equipo/<proyecto_id>

    :param form: Un objeto similar a un diccionario que contiene todos los parámetros HTTP POST dados.
    :type form: QueryDict

    :param request_user: Objeto de tipo Usuario del cual se realizo la peticion HTTP
    :type request_user: Usuario

    :param proyecto_id: Id del proyecto que se recibe por URL
    :type proyecto_id: int

    :return: Se retorna una respuesta HttpResponse que puede ser un 403 en caso de no tener la autorizacion, 422 en caso que el formulario tenga datos erroneos o retornar a la pagina principal
    :rtype: HttpResponse
    """

    if not tiene_rol_en_proyecto(request_user, "Scrum Master", proyecto_id):
        return HttpResponse('Usuario no posee el permiso de realizar esta accion', status=403)

    try:

        usuario_email = form.get('usuario_a_sacar_rol')
        rol_id = form.get('rol_id')
        usuario_a_eliminar_rol = Usuario.objects.get(email=usuario_email)
        rol = RolProyecto.objects.get(id=rol_id)
        usuario_a_eliminar_rol.roles_proyecto.remove(rol)

    except Usuario.DoesNotExist:
        return HttpResponse('Usuario no existe', status=422)

    return redirect(f'/usuarios/equipo/{proyecto_id}')


def asignar_rol_proyecto(form, request_user, proyecto_id):
    """Asignar un rol de proyecto a un usuario

    :param form: Un objeto similar a un diccionario que contiene todos los parámetros HTTP POST dados.
    :type form: QueryDict

    :param request_user: Objeto de tipo Usuario del cual se realizo la peticion HTTP
    :type request_user: Usuario

    :param proyecto_id: Id del proyecto que se recibe por URL
    :type proyecto_id: int

    :return: Se retorna una respuesta HttpResponse que puede ser un 403 en caso de no tener la autorizacion, 422 en caso que el formulario tenga datos erroneos o retornar a la pagina principal
    :rtype: HttpResponse
    """

    if not tiene_rol_en_proyecto(request_user, "Scrum Master", proyecto_id):
        return HttpResponse('Usuario no posee el permiso de realizar esta accion', status=403)

    try:

        usuario_email = form.get('usuario_a_cambiar_rol')
        rol_id = form.get(f'roles{usuario_email}')
        usuario_a_agregar_rol = Usuario.objects.get(email=usuario_email)
        rol = RolProyecto.objects.get(id=rol_id)
        usuario_a_agregar_rol.roles_proyecto.add(rol)

    except Usuario.DoesNotExist:
        return HttpResponse('Usuario no existe', status=422)

    return redirect(f'/usuarios/equipo/{proyecto_id}')


@never_cache
def listar_proyectos(request):
    """Vista de listar los proyectos de un usuario, funcion que maneja el endpoint /usuarios/equipo

    :param request: Solicitud HTTP del cliente
    :type request: HttpRequest

    :return: Se retorna una respuesta HttpResponse o 401 en caso de no estar autenticado
    :rtype: HttpResponse
    """
    if not request.user.is_authenticated:
        return HttpResponse('Usuario no autenticado', status=401)

    return render(request, 'usuarios_equipos/listar_proyectos.html')


class UsuarioForm(ModelForm):
    """
    Clase que representa el formulario de usuario. Ver Django ModelForm documentación para más información.
    """
    class Meta:
        model = Usuario
        fields = ['email', 'first_name', 'last_name', 'direccion', 'telefono', 'avatar_url']

    def __init__(self, *args, **kwargs):
        super(UsuarioForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


@never_cache
def perfil(request):
    """
    Vista para el perfil de usuario con form para editar datos.

    :param request: El request del cliente. Get en caso de quere visualizar y post en caso de querer editar.
    :type request: HttpRequest

    :return: Se retorna una respuesta HttpResponse que muestra la página actualizada con código 200 en caso exitoroso,
        401 si no se encuentra logueado o 422 si el formulario no fue llenado correctamente.
    :rtype: HttpResponse
    """
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/", status=401)

    status = 200
    if request.method == "POST":
        form = UsuarioForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/perfil/')
        else:
            status = 422

    perfil_form = UsuarioForm(instance=request.user)
    return render(request, 'socialaccount/perfil.html', {"perfil_form": perfil_form}, status=status)
