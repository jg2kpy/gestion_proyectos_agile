from django import template
from usuarios.models import Rol

register = template.Library()


@register.simple_tag
def tiene_rol_en(usuario, nombre_rol, proyecto):
    if proyecto == "":
        rol = Rol.objects.get(nombre=nombre_rol, proyecto__isnull=True)
    else:
        rol = Rol.objects.get(name=nombre_rol, proyecto=proyecto)
    return True if rol in usuario.roles.all() else False
