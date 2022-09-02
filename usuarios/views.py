from django.shortcuts import render

# Create your views here.

def rol_globl(request):

    return render(request, 'rol_global/rol_global.html', {})