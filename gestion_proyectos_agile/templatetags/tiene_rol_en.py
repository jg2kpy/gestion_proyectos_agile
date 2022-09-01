from django import template
from usuarios.models import RolSistema, RolProyecto, Usuario

register = template.Library()


@register.simple_tag
def tiene_rol_en_sistema(usuario, nombre_rol):
    rol = RolSistema.objects.get(nombre=nombre_rol)
    return True if rol in usuario.roles_sistema.all() else False


@register.simple_tag
def tiene_rol_en_proyecto(usuario, nombre_rol, proyecto):
    if proyecto == "":
        rol = RolProyecto.objects.get(nombre=nombre_rol, proyecto__isnull=True)
    else:
        rol = RolProyecto.objects.get(nombre=nombre_rol, proyecto=proyecto)
    return True if rol in usuario.roles_proyecto.all() else False



@register.simple_tag
def obtener_rol_en_proyecto(usuario, proyecto):
    return usuario.roles_proyecto.filter(proyecto = proyecto)

@register.simple_tag
def tiene_todos_los_roles(usuario, proyecto):
    return set(usuario.roles_proyecto.all()) != set(proyecto.proyecto_rol.all())
