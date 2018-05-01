from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

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


def CadastroAluno(request):
    form = FormularioCadastroAluno(request.POST or None)
    aluno = Aluno()
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['cpf']
        usuario = User.objects.create_user(username)
        aluno.user_ptr_id =usuario.id
        aluno.user = usuario
        aluno.username = form.cleaned_data['first_name']
        aluno.username = form.cleaned_data['cpf']
        aluno.email = form.cleaned_data['email']
        aluno.set_password(form.cleaned_data['password'])
        aluno.user_id = usuario.id
        aluno.curso = form.cleaned_data['curso']
        aluno.endereco = ','+','+','+','
        aluno.cpf = form.cleaned_data['cpf']
        aluno.user.groups = Group.objects.filter(name='Aluno')
        aluno.save()
        return HttpResponseRedirect('/home/')
    return render(request, 'sva/CadastroAluno.html', {'form': form})

@login_required(login_url='/accounts/login/')
def EditarAluno(request,pk):
    aluno = get_object_or_404(Aluno,pk=pk)
    texto = aluno.endereco
    Parte= texto.split(",")
    Nome = aluno.first_name+' '+aluno.last_name
    if request.method == 'POST':
        form = FormularioEditarAluno(request.POST,instance=aluno,initial={'Rua':Parte[0],'Numero':Parte[1],'Complemento':Parte[2],'Cidade':Parte[3],'Estado':Parte[4],'Nome_Completo':Nome})
        if form.is_valid():
            aluno.curso = form.cleaned_data['curso']
            aluno.telefone =  form.cleaned_data['telefone']
            texto = form.cleaned_data['Nome_Completo']
            Nome = texto.split(" ",1)
            aluno.first_name = Nome[0]
            aluno.last_name = Nome[1]
            aluno.endereco = form.cleaned_data['Rua'] + ',' + form.cleaned_data['Numero'] + ',' +  form.cleaned_data['Complemento'] + ',' +  form.cleaned_data['Cidade'] + ',' +  form.cleaned_data['Estado']
            aluno.save()
            messages.success(request, 'Editado com sucesso')
    else:
        form = FormularioEditarAluno(instance=aluno,initial={'Rua':Parte[0],'Numero':Parte[1],'Complemento':Parte[2],'Cidade':Parte[3],'Estado':Parte[4],'Nome_Completo':Nome})
    return render(request, 'sva/EditarAluno.html', {'form': form})

@login_required(login_url='/accounts/login/')
def ExcluirAluno(request,pk):
    aluno = get_object_or_404(Aluno, pk=pk)
    if aluno != None:
        aluno.is_active=False
        aluno.save()
        return HttpResponseRedirect('/home/')

def ExibirAluno(request,pk):
    aluno = get_object_or_404(Aluno, pk=pk)
    return render(request, 'sva/Perfil.html', {'nome':aluno.first_name+' '+aluno.last_name,'email':aluno.email,'telefone':aluno.telefone})
