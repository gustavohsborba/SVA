from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *

# Create your views here.

def pagina_base(request):
    context = {}
    context['cursos'] = Curso.objects.all()
    return render(request, 'sva/base.html', context)

def formulario_contato(request):
    form = FormularioContato()
    return render(request, 'sva/contato.html', {'form': form})

def PrincipalVaga(request):
    return render(request, 'sva/vaga.html')

def GerenciarVaga(request):
    context = {}
    context['vagas'] = Vaga.objects.all()
    return render(request, 'sva/gerenciarVaga.html', context)

def CriarVaga(request):

    if request.method == 'POST':
        form = FormularioCriarVaga(request.POST)
        if form.is_valid():
            form.save(commit=False)
            form.user = request.user
            form.save()
            return redirect('vaga_principal')
    else:
        form = FormularioCriarVaga()
    return render(request, 'sva/criarVaga.html', {'form': form})

def EditarVaga(request, pkvaga):

    vaga = get_object_or_404(Vaga, id=pkvaga)
    return render(request, 'sva/editarVaga.html', {'vaga': vaga})

