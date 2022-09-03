from django.shortcuts import render

from usuarios.models import RolSistema, Usuario
from django import forms
from django.shortcuts import redirect

# Crea forms
class RolSistemaForm(forms.ModelForm):
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

def rol_global_usuarios(request, id):
    rol = RolSistema.objects.get(id=id)

    if request.method == 'POST':
        nombreUsr = request.POST.get('usuarios')

        if not nombreUsr:
            estado = 'vacio'
            return render(request, 'rol_global/rol_global_validacion.html', {'estado': estado})
        
        usuario = Usuario.objects.get(username=nombreUsr)
        
        if 'vincular' in request.POST:
            if usuario.roles_sistema.filter(id=id).exists():
                estado = 'posee_rol'
                
            else:
                usuario.roles_sistema.add(rol)
                estado = 'vinculado'
            
            return render(request, 'rol_global/rol_global_validacion.html', {'estado': estado, 'usuario': usuario, 'rol': rol})

        else:
            if usuario.roles_sistema.filter(id=id).exists():
                usuario.roles_sistema.remove(rol)
                estado = 'desvinculado'
                
            else:
                estado = 'rol_inexistente'
            
            return render(request, 'rol_global/rol_global_validacion.html', {'estado': estado, 'usuario': usuario, 'rol': rol})

    else:
        usuarios = Usuario.objects.all()
        return render(request, 'rol_global/rol_global_usuarios.html', {'id': id, 'usuarios': usuarios, 'rol': rol})
