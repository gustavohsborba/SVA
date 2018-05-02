# -*- coding: utf-8 -*-

from django.contrib import messages
from datetime import date, datetime
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
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

@login_required
@user_passes_test(isGerenteVaga, login_url="/home/")
def PrincipalVaga(request):

    return render(request, 'sva/vaga.html')

@login_required
@user_passes_test(isGerenteVaga, login_url="/home/")
def GerenciarVaga(request):

    context = {}
    gerente = GerenteVaga.objects.get(user=request.user)
    if gerente is None:
        return redirect("login")
    context['vagas'] = Vaga.objects.filter(gerente_vaga_id=gerente.user_ptr_id).order_by('-data_aprovacao','-data_submissao')
    return render(request, 'sva/gerenciarVaga.html', context)

@login_required
@user_passes_test(isGerenteVaga, login_url="/home/")
def CriarVaga(request):

    gerente = GerenteVaga.objects.get(user=request.user)
    if gerente is None:
        return redirect(PrincipalVaga)

    if request.method == 'POST':
        form = FormularioVaga(request.POST)
        if form.is_valid():
            form.save(commit=False)
            gerente = GerenteVaga.objects.get(user=request.user)
            if gerente is None:
                return redirect(PrincipalVaga)
            form.instance.gerente_vaga = gerente
            form.save()
            return redirect('vaga_principal')
    else:
        form = FormularioVaga()
    return render(request, 'sva/criarVaga.html', {'form': form})

@login_required
@user_passes_test(isGerenteVaga, login_url="/home/")
def AlunosVaga(request, pkvaga):
    gerente = GerenteVaga.objects.get(user=request.user)
    if gerente is None:
        return redirect(PrincipalVaga)

    vaga = get_object_or_404(Vaga, id=pkvaga)

    if vaga.gerente_vaga_id == gerente.user_ptr_id:
        context = {}
        context['alunos'] = Aluno.objects.filter(vagas_inscritas = vaga)
        context['vaga'] = vaga
        return render(request, 'sva/ListarAlunosVaga.html', context)

    else:
        return redirect(PrincipalVaga)

@login_required
@user_passes_test(isGerenteVaga, login_url="/home/")
def EncerrarInscricaoVaga(request, pkvaga):

    gerente = GerenteVaga.objects.get(user=request.user)
    if gerente is None:
        return redirect(PrincipalVaga)

    vaga = get_object_or_404(Vaga, pk=pkvaga)
    if vaga != None and vaga.gerente_vaga_id == gerente.user_ptr_id:
        vaga.data_validade = datetime.now()
        vaga.situacao = 4
        vaga.save()
        return redirect(GerenciarVaga)
    else:
        return redirect(PrincipalVaga)

def VisualizarVaga(request, pkvaga):

    context = {}
    vaga = get_object_or_404(Vaga, id=pkvaga)
    context['vaga'] = vaga
    gerente = GerenteVaga.objects.get(vagas=vaga)
    context['gerente'] = gerente

    return render(request, 'sva/visualizarVaga.html', context)

@login_required
@user_passes_test(isGerenteVaga, login_url="/home/")
def EditarVaga(request, pkvaga):

    gerente = GerenteVaga.objects.get(user=request.user)
    if gerente is None:
        return redirect(PrincipalVaga)
    vaga = get_object_or_404(Vaga, id=pkvaga)

    if vaga.gerente_vaga_id == gerente.user_ptr_id:

        if request.method == 'POST':
            form = FormularioVaga(request.POST, instance=vaga)
            if form.is_valid():
                vaga.areas_atuacao = form.cleaned_data['areas_atuacao']
                vaga.titulo = form.cleaned_data['titulo']
                vaga.descricao = form.cleaned_data['descricao']
                vaga.data_validade = form.cleaned_data['data_validade']
                vaga.carga_horaria_semanal = form.cleaned_data['carga_horaria_semanal']
                vaga.local = form.cleaned_data['local']
                vaga.valor_bolsa = form.cleaned_data['valor_bolsa']
                vaga.beneficios = form.cleaned_data['beneficios']
                vaga.situacao = 2;
                vaga.save()
                return redirect(GerenciarVaga)

        else:
            form = FormularioVaga(instance=vaga)
            return render(request, 'sva/editarVaga.html', {'form': form})

    else:
        return redirect(PrincipalVaga)

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



def layout(request):
    form = FormularioContato()
    return render(request, 'sva/layout.html', {'form': form})


def RecuperarSenha(request):
    if request.method == "POST":
        cpf = request.POST['CPF']
        email = request.POST['email']

        user = Aluno.objects.filter(User.objects.get(email=email),Aluno.objects.get(cpf=cpf))
        if user is not None:
            if user.is_authenticated:
                return HttpResponseRedirect('/')
            else:
                messages.error(request, '1Combinação de CPF e email invalida')
                return HttpResponseRedirect('')
        else:
            messages.error(request, 'Combinação de CPF e email invalida')
            return HttpResponseRedirect('')
    return render(request, 'registration/recuperarSenha.html', {})

