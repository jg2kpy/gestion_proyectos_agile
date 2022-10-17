from django import template
from historias_usuario.models import HistoriaUsuario
from usuarios.models import RolSistema, RolProyecto, Usuario
from proyectos.models import Proyecto, Sprint

"""
Los templares tags son funciones en python que podemos ejecutar en los templates HTML
"""

register = template.Library()


@register.simple_tag
def tiene_rol_en_sistema(usuario, nombre_rol):
    """Funcion para verificar si un usuario tiene un rol de sistema

    :param usuario: Objeto usuario del cual se verifica 
    :type usuario: Usuario

    :param nombre_rol: Nombre del rol del cual vamos a verificar
    :type nombre_rol: str

    :return: Se retorna un valor True si el usuario tiene el rol en el sistema o False en caso contrario
    :rtype: boolean
    """
    rol = RolSistema.objects.get(nombre=nombre_rol)
    return True if rol in usuario.roles_sistema.all() else False


@register.simple_tag
def tiene_rol_en_proyecto(usuario, nombre_rol, proyecto):
    """Funcion para verificar si un usuario tiene un rol de proyecto

    :param usuario: Objeto usuario del cual se verifica 
    :type usuario: Usuario

    :param nombre_rol: Nombre del rol del cual vamos a verificar
    :type nombre_rol: str

    :param proyecto: Proyecto donde se verficara si el usuario tiene el rol en este proyecto
    :type proyecto: Proyecto

    :return: Se retorna un valor True si el usuario tiene el rol en el proyecto indicado o False en caso contrario
    :rtype: boolean
    """
    try:
        if proyecto == "":
            rol = RolProyecto.objects.get(
                nombre=nombre_rol, proyecto__isnull=True)
        else:
            rol = RolProyecto.objects.get(nombre=nombre_rol, proyecto=proyecto)
        return True if rol in usuario.roles_proyecto.all() else False
    except RolProyecto.DoesNotExist:
        return False


@register.simple_tag
def obtener_rol_en_proyecto(usuario, proyecto):
    """Funcion para obtener la lista total de roles de un usuario en un proyecto especifico

    :param usuario: Objeto usuario del cual se verifica 
    :type usuario: Usuario

    :param proyecto: Proyecto donde se verifica si el usuario tiene el rol en este proyecto
    :type proyecto: Proyecto

    :return: Se retorna la lista de los Roles de Proyecto de un usuario en el proyecto especifico
    :rtype: QuerySet<RolProyecto>
    """
    return usuario.roles_proyecto.filter(proyecto=proyecto)


@register.simple_tag
def tiene_todos_los_roles(usuario, proyecto):
    """Funcion para verificar si un usuario tiene todos los roles en su proyecto 

    :param usuario: Objeto usuario del cual se verifica 
    :type usuario: Usuario

    :param proyecto: Proyecto donde se verifica si el usuario tiene todos los roles
    :type proyecto: Proyecto

    :return: Se retorna un valor True si el usuario tiene todos los roles en el proyecto indicado o False en caso contrario
    :rtype: boolean
    """
    return set(usuario.roles_proyecto.filter(proyecto=proyecto)) != set(proyecto.roles.all())


@register.simple_tag
def obtener_proyecto(proyecto_id):
    """Funcion para obtener el objeto proyecto mediante su id en un template 

    :param proyecto_id: Id del proyecto
    :type proyecto_id: int

    :return: El objeto proyecto del id dado
    :rtype: Proyecto
    """
    return Proyecto.objects.get(id=proyecto_id)


@register.simple_tag
def tiene_permiso_en_proyecto(usuario, permiso, proyecto):
    """Funcion para verificar si un usuario tiene un permiso en un proyecto 

    :param usuario: Objeto usuario del cual se verifica 
    :type usuario: Usuario

    :param permiso: Nombre del permiso a verificar
    :type permiso: String

    :param proyecto: Proyecto donde se verifica si el usuario tiene el permiso en este proyecto
    :type proyecto: Proyecto

    :return: Se retorna un valor True si el usuario tiene el permiso en el proyecto indicado o False en caso contrario
    :rtype: boolean
    """
    return usuario.roles_proyecto.filter(proyecto=proyecto).filter(permisos__nombre=permiso).exists()


@register.simple_tag
def tiene_permiso_en_sistema(usuario, permiso):
    """Funcion para verificar si un usuario tiene un permiso en el sistema 

    :param usuario: Objeto usuario del cual se verifica 
    :type usuario: Usuario

    :param permiso: Nombre del permiso a verificar
    :type permiso: String

    :return: Se retorna un valor True si el usuario tiene el permiso en el proyecto indicado o False en caso contrario
    :rtype: boolean
    """
    return usuario.roles_sistema.filter(permisos__nombre=permiso).exists()


@register.simple_tag
def siguente_etapa(historia):
    """Funcion para determinar la siguente etapa de un historia de usuario

    :param historia: Objeto historia a determinar su siguente etapa
    :type usuario: historia

    :return: Se retorna el nombre de la siguente etapa o en caso de ser la ultima, se retorna 'terminado'
    :rtype: str
    """
    siguiente = historia.etapa.orden + 1 if historia.etapa else 0
    return historia.tipo.etapas.all()[siguiente].nombre if siguiente < historia.tipo.etapas.count() else 'terminado'


@register.simple_tag
def anterior_etapa(historia):
    """Funcion para determinar la etapa anterior de un historia de usuario

    :param historia: Objeto historia a determinar su etapa anterior
    :type usuario: historia

    :return: Se retorna el nombre de la etapa anterior
    :rtype: str
    """
    anterior = historia.etapa.orden - 1 if historia.etapa and historia.etapa.orden > 1 else 0
    return historia.tipo.etapas.all()[anterior].nombre


@register.simple_tag
def lista_adm():
    """Funcion que retorna una lista de los administradores

    :return: Se retorna una lista con los administradores
    :rtype: list
    """
    adminRol = RolSistema.objects.get(nombre="gpa_admin")
    return adminRol.usuario.all()

@register.simple_tag

def check_sprint_desarrollo(cookieIndice, sprints):
    """Funcion para determinar si un sprint se encuentra en desarrollo
    :param cookieIndice: Indice guardado en cookie
    :type cookieIndice: str

    :param sprints: Lista con los sprints disponibles
    :type sprints: list

    :return: Se retorna True si está en desarrollo caso contrario False
    :rtype: bool
    """
    
    if cookieIndice:
        return sprints[int(cookieIndice)].estado == "Desarrollo"
    else:
        return sprints[0].estado == "Desarrollo"

@register.simple_tag
def check_sprint_no_planificacion(tablero):
    """Funcion para verificar si existe un sprint en desarrollo o ya terminado para el tablero
    :param tablero: Objeto del tipo de historia
    :type tablero: TipoHistoriaUsusario

    :return: Se retorna True si existe un sprint en desarrollo o ya terminado
    :rtype: bool
    """
    sprints = Sprint.objects.filter(proyecto=tablero.proyecto, historias__tipo=tablero).exclude(fecha_inicio__isnull=True)
    
    if sprints:
        return True
    else:
        return False

@register.simple_tag
def check_sprint_activo(proyecto):
    """Funcion para verificar si existe un sprint en desarrollo
    :param proyecto: Objeto del proyecto
    :type proyecto: Proyecto

    :return: Se retorna True si existe un sprint en desarrollo
    :rtype: bool
    """
    sprints = Sprint.objects.filter(proyecto=proyecto, estado="Desarrollo").exclude(fecha_inicio__isnull=True)
    
    if sprints:
        return True
    else:
        return False

@register.simple_tag
def check_historia_activa(proyecto, sprints):
    """Funcion para determinar si existe una historia de usuario activa en el sprint más reciente

    :param proyecto: Objeto del proyecto
    :type proyecto: Proyecto

    :param sprints: Lista con los sprints disponibles
    :type sprints: list

    :return: Se retorna True si encuentra una historia de usuario no terminada
    :rtype: bool
    """
    historiasActivas = HistoriaUsuario.objects.filter(proyecto=proyecto, sprint=sprints[0], estado='A')

    if historiasActivas:
        return True
    else:
        return False

@register.simple_tag
def es_miembro(usuario, proyecto):
    """Funcion para verificar que un miembro pertenece a un proyecto

    :return: True si el usuario es miembro del proyecto
    :rtype: bool
    """
    return usuario.equipo.filter(id=proyecto.id).exists()
