from django.http import HttpResponseRedirect
from django.shortcuts import render


from .models import *
from sva.forms import *


# Create your views here.

def pagina_base(request):
    context = {}
    context['cursos'] = Curso.objects.all()
    return render(request, 'sva/base.html', context)

def formulario_contato(request):
    form = FormularioContato()
    return render(request, 'sva/contato.html', {'form': form})


def CadastroUsuario(request):
    username = Aluno(username=request.POST.get('cpf'))
    form = FormularioCadastroAluno(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        usuario = User.objects.create_user(username)
        form.user = usuario
        #form.user.groups = Group.objects.get(name='Aluno')
        form.save();
        return HttpResponseRedirect('/home/')
    return render(request, 'sva/CadastroAluno.html', {'form': form})
