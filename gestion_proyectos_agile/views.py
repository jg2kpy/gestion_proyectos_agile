from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.shortcuts import render

from historias_usuario.models import ArchivoAnexo, HistoriaUsuario 
from django.shortcuts import render, redirect
from django.http import FileResponse, HttpResponse, HttpResponseRedirect


class NeverCacheMixin(object):
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(NeverCacheMixin, self).dispatch(*args, **kwargs)


class Home(NeverCacheMixin, TemplateView):
    template_name = 'home.html'

def error_404_view(request, exception):
   
    # we add the path to the the 404.html file
    # here. The name of our HTML file is 404.html
    return render(request, '404.html', status=404)


@never_cache
def descargar(request, archivo_id):
    """
    Permite descargar un archivo.

    :param request: HttpRequest
    :type request: HttpRequest
    :param archivo_id: Id del archivo a descargar
    :type archivo_id: int
    :rtype: HttpResponse
    """
    if not request.user.is_authenticated:
        return HttpResponse('Usuario no autorizado', status=401)

    try:
        archivo = ArchivoAnexo.objects.get(id=archivo_id)
    except ArchivoAnexo.DoesNotExist:
        return render(request, '404.html', {'info_adicional': "No se encontró este archivo."}, status=404)

    if not archivo.historia_usuario.get(estado=HistoriaUsuario.Estado.ACTIVO).proyecto.usuario.filter(id=request.user.id).exists():
        return render(request, '403.html', {'info_adicional': "No tiene permisos para descargar este archivo."}, status=403)
    
    return FileResponse(open(archivo.archivo.path, 'rb'), content_type='application/force-download')
