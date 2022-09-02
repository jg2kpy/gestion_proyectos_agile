from django.shortcuts import render

from usuarios.models import RolSistema
from django import forms
from django.shortcuts import redirect

# Crea forms
class RolSistemaForm(forms.ModelForm):
     class Meta:
        model = RolSistema
        # fields = '__all__'
        exclude = ('usuario',)

# Create your views here.

def rol_global_list(request):
    roles = RolSistema.objects.all()
    return render(request, 'rol_global/rol_global_list.html', {'roles': roles})

def rol_global_info(request, id):
    rol = RolSistema.objects.get(id=id)
    return render(request, 'rol_global/rol_global_info.html', {'rol': rol})

def rol_global_crear(request):
    if request.method == 'POST':
        form = RolSistemaForm(request.POST)
        
        if form.is_valid():
            rol = form.save()
            return redirect('rol_global_info', rol.id)

    else:
        form = RolSistemaForm()

    return render(request, 'rol_global/rol_global_crear.html', {'form': form})

def rol_global_editar(request, id):
    rol = RolSistema.objects.get(id=id)
    
    if request.method == 'POST':
        form = RolSistemaForm(request.POST, instance=rol)
    
        if form.is_valid():
            form.save()
            return redirect('rol_global_info', rol.id)

    else:
        form = RolSistemaForm(instance=rol)

    return render(request, 'rol_global/rol_global_editar.html', {'form': form})

def rol_global_eliminar(request, id):
    rol = RolSistema.objects.get(id=id)

    if request.method == 'POST':
        rol.delete()
        return redirect('rol_global_list')
        
    return render(request, 'rol_global/rol_global_eliminar.html', {'rol': rol})


