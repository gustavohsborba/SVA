# -*- coding: utf-8 -*-

from django.contrib import messages
from datetime import date, datetime
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from sva import mensagens
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
def principal_vaga(request):
    return render(request, 'sva/vaga/vaga.html')


@login_required
@user_passes_test(isGerenteVaga, login_url="/home/")
def gerenciar_vaga(request):
    context = {}
    gerente = GerenteVaga.objects.get(user=request.user)
    if gerente is None:
        return redirect("login")
    context['vagas'] = Vaga.objects.filter(gerente_vaga_id=gerente.user_ptr_id).order_by('-data_aprovacao','-data_submissao')
    return render(request, 'sva/vaga/gerenciarVaga.html', context)


@login_required
@user_passes_test(isGerenteVaga, login_url="/home/")
def criar_vaga(request):
    gerente = GerenteVaga.objects.get(user=request.user)
    if gerente is None:
        messages.error(request, mensagens.ERRO_PERMISSAO_NEGADA, mensagens.MSG_ERRO)
        return redirect(principal_vaga)

    if request.method == 'POST':
        form = FormularioVaga(request.POST)
        if form.is_valid():
            form.save(commit=False)
            gerente = GerenteVaga.objects.get(user=request.user)
            if gerente is None:
                messages.error(request, mensagens.ERRO_PERMISSAO_NEGADA, mensagens.MSG_ERRO)
                return redirect(principal_vaga)
            form.instance.gerente_vaga = gerente
            form.save()
            return redirect('vaga_principal')
    else:
        form = FormularioVaga()
    return render(request, 'sva/vaga/criarVaga.html', {'form': form})


@login_required
@user_passes_test(isGerenteVaga, login_url="/home/")
def lista_alunos_vaga(request, pkvaga):
    gerente = GerenteVaga.objects.get(user=request.user)
    if gerente is None:
        messages.error(request, mensagens.ERRO_PERMISSAO_NEGADA, mensagens.MSG_ERRO)
        return redirect(principal_vaga)

    vaga = get_object_or_404(Vaga, id=pkvaga)

    if vaga.gerente_vaga_id == gerente.user_ptr_id:
        context = {}
        context['alunos'] = Aluno.objects.filter(vagas_inscritas=vaga)
        context['vaga'] = vaga
        return render(request, 'sva/vaga/ListarAlunosVaga.html', context)

    else:
        messages.error(request, mensagens.ERRO_PERMISSAO_NEGADA, mensagens.MSG_ERRO)
        return redirect(principal_vaga)


@login_required
@user_passes_test(isGerenteVaga, login_url="/home/")
def encerrar_inscricao_vaga(request, pkvaga):
    gerente = GerenteVaga.objects.get(user=request.user)
    if gerente is None:
        messages.error(request, mensagens.ERRO_PERMISSAO_NEGADA, mensagens.MSG_ERRO)
        return redirect(principal_vaga)

    vaga = get_object_or_404(Vaga, pk=pkvaga)
    if vaga is None or vaga.gerente_vaga_id != gerente.user_ptr_id:
        messages.error(request, mensagens.ERRO_PERMISSAO_NEGADA, mensagens.MSG_ERRO)
        return redirect(principal_vaga)
    else:
        vaga.data_validade = datetime.now()
        vaga.situacao = 4
        vaga.save()
        return redirect(gerenciar_vaga)


def visualizar_vaga(request, pkvaga):

    context = {}
    vaga = get_object_or_404(Vaga, id=pkvaga)
    context['vaga'] = vaga
    gerente = GerenteVaga.objects.get(vagas=vaga)
    context['gerente'] = gerente

    return render(request, 'sva/vaga/visualizarVaga.html', context)


@login_required
@user_passes_test(isGerenteVaga, login_url="/home/")
def editar_vaga(request, pkvaga):

    gerente = GerenteVaga.objects.get(user=request.user)
    if gerente is None:
        messages.error(request, mensagens.ERRO_PERMISSAO_NEGADA, mensagens.MSG_ERRO)
        return redirect(principal_vaga)
    vaga = get_object_or_404(Vaga, id=pkvaga)

    if vaga.gerente_vaga_id != gerente.user_ptr_id:
        messages.error(request, mensagens.ERRO_PERMISSAO_NEGADA, mensagens.MSG_ERRO)
        return redirect(principal_vaga)

    if request.method == 'GET':
        form = FormularioVaga(instance=vaga)
        return render(request, 'sva/vaga/editarVaga.html', {'form': form})

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
        return redirect(gerenciar_vaga)


def cadastro(request):
    context = {
        'form_aluno': FormularioCadastroAluno(),
        'form_professor': FormularioCadastroProfessor(),
        'form_empresa': FormularioCadastroEmpresa()
    }
    return render(request, 'sva/cadastro.html', context)


@transaction.atomic
def cadastrar_aluno(request):
    form = FormularioCadastroAluno(request.POST or None)
    aluno = Aluno()
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['cpf']
        usuario = User.objects.create_user(username)
        aluno.user_ptr_id =usuario.id
        aluno.user = usuario
        aluno.user.username = form.cleaned_data['cpf']
        aluno.user.email = form.cleaned_data['email']
        aluno.user.set_password(form.cleaned_data['password'])
        aluno.user.save()
        aluno.curso = form.cleaned_data['curso']
        aluno.endereco = ','+','+','+','
        aluno.cpf = form.cleaned_data['cpf']
        aluno.user.groups = Group.objects.filter(name='Aluno')
        aluno.save()
        return HttpResponseRedirect('/home/')
    return render(request, 'sva/aluno/CadastroAluno.html', {'form': form})


@transaction.atomic
@login_required(login_url='/accounts/login/')
def editar_aluno(request, pk):
    aluno = get_object_or_404(Aluno,pk=pk)
    texto = aluno.endereco
    Parte= texto.split(",")
    Nome = aluno.user.first_name+' '+aluno.user.last_name
    initial = {'Rua': Parte[0],
               'Numero': Parte[1],
               'Complemento': Parte[2],
               'Cidade': Parte[3],
               'Estado': Parte[4],
               'Nome_Completo': Nome}
    if request.method == 'POST':
        form = FormularioEditarAluno(request.POST,instance=aluno,initial=initial)
        if form.is_valid():
            aluno.curso = form.cleaned_data['curso']
            aluno.telefone =  form.cleaned_data['telefone']
            texto = form.cleaned_data['Nome_Completo']
            Nome = texto.split(" ",1)
            aluno.endereco = form.cleaned_data['Rua'] + ',' + \
                             form.cleaned_data['Numero'] + ',' +  \
                             form.cleaned_data['Complemento'] + ',' +  \
                             form.cleaned_data['Cidade'] + ',' +  \
                             form.cleaned_data['Estado']
            aluno.save()
            aluno.user.first_name = Nome[0]
            aluno.user.last_name = Nome[1]
            aluno.user.save()
            messages.success(request, 'Editado com sucesso')
    else:
        form = FormularioEditarAluno(instance=aluno,initial=initial)
    return render(request, 'sva/aluno/EditarAluno.html', {'form': form})


@login_required(login_url='/accounts/login/')
def excluir_aluno(request, pk):
    aluno = get_object_or_404(Aluno, pk=pk)
    if aluno is not None:
        aluno.user.is_active = False
        aluno.user.save()
        messages.error(request, mensagens.SUCESSO_ACAO_CONFIRMADA, mensagens.MSG_SUCCESS)
        return HttpResponseRedirect('/home/')


def exibir_aluno(request, pk):
    aluno = get_object_or_404(Aluno, pk=pk)
    context = {'aluno': aluno}
    return render(request, 'sva/aluno/Perfil.html', context)


def layout(request):
    form = FormularioContato()
    return render(request, 'sva/layout.html', {'form': form})


def recuperar_senha(request):
    if request.method == "GET":
        return render(request, 'registration/recuperarSenha.html', {})

    cpf = request.POST['CPF']
    email = request.POST['email']
    user = Aluno.objects.filter(user__email=email, cpf=cpf)

    if user is not None:
        if user.is_authenticated:
            return HttpResponseRedirect('/')
        else:
            messages.error(request, mensagens.ERRO_COMBINACAO_CPF_EMAIL_INVALIDA, mensagens.MSG_ERRO)
            return HttpResponseRedirect('')
    else:
        messages.error(request, mensagens.ERRO_COMBINACAO_CPF_EMAIL_INVALIDA, mensagens.MSG_ERRO)
        return HttpResponseRedirect('')

