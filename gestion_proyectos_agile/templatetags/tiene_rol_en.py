from django import template
from usuarios.models import RolSistema, RolProyecto

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
