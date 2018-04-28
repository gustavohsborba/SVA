from django.shortcuts import render
from .models import *
from sva.forms import *
from django.views.generic import CreateView

# Create your views here.

def pagina_base(request):
    context = {}
    context['cursos'] = Curso.objects.all()
    return render(request, 'sva/base.html', context)

def formulario_contato(request):
    form = FormularioContato()
    return render(request, 'sva/contato.html', {'form': form})


class Criar(CreateView):
    template_name = 'sva/CadastroAluno.html'
    model = Aluno
    fields = ['cpf', 'email', 'password']

