from django import template
from usuarios.models import RolSistema, RolProyecto, Usuario
from proyectos.models import Proyecto

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
    return set(usuario.roles_proyecto.filter(proyecto=proyecto)) != set(proyecto.proyecto_rol.all())


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
