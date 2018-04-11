from django.shortcuts import render
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
