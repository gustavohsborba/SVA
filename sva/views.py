from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import *
from .forms import *

# Create your views here.

@login_required
def home(request):
    context = {}
    context['cursos'] = Curso.objects.all()
    return render(request, 'sva/base.html', context)

def formulario_contato(request):
    form = FormularioContato()
    return render(request, 'sva/contato.html', {'form': form})

def cadastro(request):
    context = {
        'form_aluno': FormularioCadastroAluno(),
        'form_professor': FormularioCadastroProfessor(),
        'form_empresa': FormularioCadastroEmpresa()
    }
    return render(request, 'sva/cadastro.html', context)


def layout(request):
    form = FormularioContato()
    return render(request, 'sva/layout.html', {'form': form})