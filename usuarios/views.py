from django.shortcuts import render


def perfil(request):

    if request.method == "POST":
        # reservado para cuando quiere editar su perfil
        pass
    return render(request, 'socialaccount/perfil.html')
