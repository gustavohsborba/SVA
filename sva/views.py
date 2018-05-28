# -*- coding: utf-8 -*-
from typing import Dict, Any, Union

from django.contrib import messages
from django.db.models.functions import Concat
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.db import transaction
from django.db.models import Q, Value
from datetime import datetime
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
import string
from random import choice

from django.views.decorators.http import require_POST

from sva import mensagens
from .models import *
from .forms import *


def is_admin(user):
    if user.is_superuser:
        return True
    if user.groups.filter(name='Administrador').exists():
        return True
    if user.groups.filter(name='Setor de Estágios').exists():
        return True
    return False


# Create your views here.


@login_required
def home(request):
    return render(request, 'sva/base.html')


def formulario_contato(request):
    form = FormularioContato()
    return render(request, 'sva/contato.html', {'form': form})


###############################################################################
#                                  VAGAS                                      #
###############################################################################

@login_required
def pesquisar_vaga(request):
    form =  FormularioPesquisaVagasAluno(request.POST)
    context = {}
    context['form']=form
    if form.is_valid():
            if form.cleaned_data['Area_Atuacao']=="":
                context['vagas'] = Vaga.objects.filter(titulo__icontains= form.cleaned_data['Vaga_Cadastrada'])
                context['busca'] = form.cleaned_data['Vaga_Cadastrada']
            elif form.cleaned_data['Vaga_Cadastrada']=="":
                areas=AreaAtuacao.objects.filter(nome__icontains= form.cleaned_data['Area_Atuacao'])
                context['busca'] = form.cleaned_data['Area_Atuacao']
                for area in areas:
                    context['vagas'] = Vaga.objects.filter(areas_atuacao=area.id)
            else:
                areas = AreaAtuacao.objects.filter(nome__icontains=form.cleaned_data['Area_Atuacao'])
                context['busca'] = form.cleaned_data['Vaga_Cadastrada']+", "+form.cleaned_data['Area_Atuacao']
                for area in areas:
                    context['vagas'] = Vaga.objects.filter(titulo__icontains= form.cleaned_data['Vaga_Cadastrada'], areas_atuacao=area.id)
    else:
        context['vagas'] = Vaga.objects.filter()
        context['busca'] = ""

    if 'buscar_keyword' in request.POST and request.POST.get('buscar_keyword') is not None and request.POST.get('buscar_keyword') != '':
        busca_rapida = request.POST.get('buscar_keyword')
        context['vagas'] = Vaga.objects.filter(titulo__icontains=busca_rapida)
        context['busca'] = request.POST.get('buscar_keyword')
    context['now']= timezone.now()
    return render(request, 'sva/vaga/pesquisarVagas.html', context)

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

    form = FormularioGerenciaVaga(request.POST)
    context['form'] = form
    if form.is_valid() and form.cleaned_data['vaga_nome']!= "":
        context['vagas'] = Vaga.objects.filter(gerente_vaga_id=gerente.id, titulo__icontains=form.cleaned_data['vaga_nome']).order_by('-data_aprovacao','-data_alteracao','-data_submissao')
    else:
        context['vagas'] = Vaga.objects.filter(gerente_vaga_id=gerente.id).order_by('-data_aprovacao','-data_alteracao','-data_submissao')
    return render(request, 'sva/vaga/gerenciarVaga.html', context)


@login_required
@transaction.atomic
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
            messages.success(request, 'Vaga criada com sucesso')
            return redirect(gerenciar_vaga)
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

    if vaga.gerente_vaga_id == gerente.id:
        context = {}
        context['alunos'] = Aluno.objects.filter(vagas_inscritas=vaga)
        context['qtd_alunos'] = Aluno.objects.filter(vagas_inscritas=vaga).count()
        context['vaga'] = vaga
        return render(request, 'sva/vaga/ListarAlunosVaga.html', context)

    else:
        messages.error(request, mensagens.ERRO_PERMISSAO_NEGADA, mensagens.MSG_ERRO)
        return redirect(principal_vaga)


@login_required
@transaction.atomic
@user_passes_test(isGerenteVaga, login_url="/home/")
def encerrar_inscricao_vaga(request, pkvaga):
    gerente = GerenteVaga.objects.get(user=request.user)
    if gerente is None:
        messages.error(request, mensagens.ERRO_PERMISSAO_NEGADA, mensagens.MSG_ERRO)
        return redirect(principal_vaga)

    vaga = get_object_or_404(Vaga, pk=pkvaga)
    if vaga is None or vaga.gerente_vaga_id != gerente.id:
        messages.error(request, mensagens.ERRO_PERMISSAO_NEGADA, mensagens.MSG_ERRO)
        return redirect(principal_vaga)
    else:
        vaga.data_validade = datetime.now()
        vaga.situacao = 4
        vaga.save()
        messages.success(request, 'Inscrições encerradas')
        return redirect(gerenciar_vaga)


def visualizar_vaga(request, pkvaga):
    context = {}
    vaga = get_object_or_404(Vaga, id=pkvaga)
    context['vaga'] = vaga
    gerente = GerenteVaga.objects.get(vagas=vaga)
    if(request.user.groups.filter(name='Aluno').exists()):
        aluno = Aluno.objects.get(user_id=request.user.id)
        context['aluno'] = aluno
        # Verifica se aluno logado eh interessado na vaga
        if (vaga.alunos_interessados.filter(id=aluno.id).exists()):
            context['interessado'] = 1
        else:
            context['interessado'] = 0
        #Verifica se aluno logado eh inscrito na vaga
        if(vaga.alunos_inscritos.filter(id=aluno.id).exists()):
            context['inscrito'] = 1
            context['interessado'] = 2
        else:
            context['inscrito'] = 0

    context['gerente'] = gerente
    if request.method == 'POST':
        if 'subscribe' in request.POST:
            vaga.alunos_inscritos.add(aluno)
            if (vaga.alunos_interessados.filter(id=aluno.id).exists()):
                vaga.alunos_interessados.remove(aluno)
            messages.success(request, 'Candidatado com sucesso')
            return redirect(visualizar_vaga, vaga.id)
        elif 'unsubscribe' in request.POST:
            vaga.alunos_inscritos.remove(aluno)
            messages.success(request, 'Candidatura removida com sucesso')
            return redirect(visualizar_vaga, vaga.id)
        elif 'interested' in request.POST:
            vaga.alunos_interessados.add(aluno)
            return redirect(visualizar_vaga, vaga.id)
        elif 'uninterested' in request.POST:
            vaga.alunos_interessados.remove(aluno)
            return redirect(visualizar_vaga, vaga.id)
    context['formulario_aprovacao'] = FormularioAprovacao()
    return render(request, 'sva/vaga/visualizarVaga.html', context)


@login_required
@transaction.atomic
@user_passes_test(isGerenteVaga, login_url="/home/")
def editar_vaga(request, pkvaga):
    gerente = GerenteVaga.objects.get(user=request.user)
    if gerente is None:
        messages.error(request, mensagens.ERRO_PERMISSAO_NEGADA, mensagens.MSG_ERRO)
        return redirect(principal_vaga)
    vaga = get_object_or_404(Vaga, id=pkvaga)

    if vaga.gerente_vaga_id != gerente.id:
        messages.error(request, mensagens.ERRO_PERMISSAO_NEGADA, mensagens.MSG_ERRO)
        return redirect(principal_vaga)

    if request.method == 'GET':
        form = FormularioVaga(instance=vaga)
        context = {}
        if(vaga.data_validade is not None):
            data_val = vaga.data_validade.strftime('%Y-%m-%dT%H:%M')
            context['data_val'] = data_val
        context['form'] = form
        return render(request, 'sva/vaga/editarVaga.html', context)

    form = FormularioVaga(request.POST, instance=vaga)
    if form.is_valid():
        vaga.cursos = form.cleaned_data['cursos']
        vaga.areas_atuacao = form.cleaned_data['areas_atuacao']
        vaga.titulo = form.cleaned_data['titulo']
        vaga.descricao = form.cleaned_data['descricao']
        vaga.data_validade = form.cleaned_data['data_validade']
        vaga.carga_horaria_semanal = form.cleaned_data['carga_horaria_semanal']
        vaga.local = form.cleaned_data['local']
        vaga.valor_bolsa = form.cleaned_data['valor_bolsa']
        vaga.beneficios = form.cleaned_data['beneficios']
        vaga.data_aprovacao = None
        vaga.situacao = 2
        vaga.save()
        messages.success(request, 'Editado com sucesso')
        return redirect(gerenciar_vaga)



@login_required
@user_passes_test(is_admin)
def gerenciar_vaga_pendente(request):
    if 'filtro' in request.POST and request.POST['filtro'] is not None and request.POST['filtro'] != '':
        vagas = Vaga.objects.filter(data_aprovacao__isnull=True, situacao__gte=1, situacao__lte=2, titulo__icontains=request.POST['filtro']).order_by('-data_alteracao','-data_submissao')
    else:
        vagas = Vaga.objects.filter(data_aprovacao__isnull=True, situacao__gte=1, situacao__lte=2,).order_by('-data_alteracao','-data_submissao')
    context = {
        'titulo_lista': 'Vagas com aprovação pendente',
        'liberar_cadastro': True,
        'vagas': vagas,
    }
    return render(request, 'sva/vaga/ListarVagasPendentes.html', context)


@transaction.atomic
@login_required
@require_POST
@user_passes_test(is_admin)
def aprovar_vaga(request, pkvaga):

    # TODO: Fazer isso aqui utilizar o FormularioAprovacao, como as views de aprovar_professor e aprovar_empresa
    # context['formulario_aprovacao'] = FormularioAprovacao()

    vaga = get_object_or_404(Vaga, id=pkvaga)
    if vaga is not None and request.POST['aprovado'] == 'true':
        vaga.situacao = 3
        vaga.data_aprovacao = datetime.now()
        vaga.usuario_aprovacao = request.user.first_name + ' ' + request.user.last_name
        vaga.save()
        mensagem = 'Seu cadastro da vaga %s foi aprovado no SVA por %s. Segue mensagem:\n\n %s' \
                   % (vaga.titulo, request.user.first_name, request.POST['justificativa'])
        send_mail('Avaliação de cadastro de vaga - Sistema de Vagas Acadêmicas',
                  mensagem, 'from@example.com', [vaga.gerente_vaga.user.email])
    else:
        vaga.situacao = 5
        vaga.save()
        mensagem = 'Seu cadastro da vaga %s foi recusado no SVA por %s. Segue mensagem:\n\n%s\n\nSVA' \
                   % (vaga.titulo, request.user.first_name, request.POST['justificativa'])
        send_mail('Avaliação de cadastro de vaga - Sistema de Vagas Acadêmicas',
                  mensagem, 'from@example.com', [vaga.gerente_vaga.user.email])
    messages.success(request, mensagens.SUCESSO_ACAO_CONFIRMADA, mensagens.MSG_SUCCESS)
    return redirect(visualizar_vaga, pkvaga)

###############################################################################
#                               CADASTRO                                      #
###############################################################################


def cadastro(request):
    context = {
        'form_aluno': FormularioCadastroAluno(),
        'form_professor': FormularioCadastroProfessor(),
        'form_empresa': FormularioCadastroEmpresa(),
        'cadastro': True
    }
    return render(request, 'sva/cadastro.html', context)


@transaction.atomic
def cadastrar_empresa(request):
    form = FormularioCadastroEmpresa(request.POST or None)
    empresa = Empresa()
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['cnpj']
        usuario = User.objects.create_user(username)
        empresa.user = usuario
        empresa.cnpj = form.cleaned_data['cnpj']
        empresa.nome = form.cleaned_data['nome']
        empresa.user.email = form.cleaned_data['email']
        empresa.user.set_password(form.cleaned_data['password'])
        empresa.user.groups = Group.objects.filter(Q(name='Empresa') | Q(name='Gerente Vagas'))
        empresa.user.save()
        empresa.save()
        #empresa.data_aprovacao = datetime.now()
        messages.info(request, mensagens.SUCESSO_AGUARDE_APROVACAO, mensagens.MSG_SUCCESS)
        return HttpResponseRedirect('/home/')
    return render(request, 'sva/empresa/CadastroEmpresa.html', {'form': form})


@transaction.atomic
def cadastrar_aluno(request):
    form = FormularioCadastroAluno(request.POST or None)
    aluno = Aluno()
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['cpf']
        usuario = User.objects.create_user(username)
        aluno.user = usuario
        aluno.user.username = form.cleaned_data['cpf']
        aluno.user.first_name = form.cleaned_data['first_name']
        aluno.user.last_name = ''
        aluno.user.email = form.cleaned_data['email']
        aluno.user.set_password(form.cleaned_data['password'])
        aluno.user.save()
        aluno.curso = form.cleaned_data['curso']
        aluno.endereco = ',' + ',' + ',' + ','
        aluno.cpf = form.cleaned_data['cpf']
        aluno.user.groups = Group.objects.filter(name='Aluno')
        aluno.save()
        messages.success(request, mensagens.SUCESSO_ACAO_CONFIRMADA, mensagens.MSG_SUCCESS)
        return HttpResponseRedirect('/home/')
    return render(request, 'sva/aluno/CadastroAluno.html', {'form': form})


@transaction.atomic
def cadastrar_professor(request):
    form = FormularioCadastroProfessor(request.POST or None)
    professor = Professor()
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['cpf']
        usuario = User.objects.create_user(username)
        professor.curso = form.cleaned_data['curso']
        professor.user_ptr_id = usuario.id
        professor.user = usuario
        professor.user.username = form.cleaned_data['cpf']
        professor.user.first_name = form.cleaned_data['nome']
        professor.user.email = form.cleaned_data['email']
        professor.user.set_password(form.cleaned_data['password'])
        professor.user.save()
        professor.cpf = form.cleaned_data['cpf']
        professor.siape = form.cleaned_data['siape']
        professor.user.groups = Group.objects.filter(Q(name='Professor') | Q(name='Gerente Vagas'))
        professor.save()
        messages.info(request, mensagens.SUCESSO_AGUARDE_APROVACAO, mensagens.MSG_SUCCESS)
        return redirect('login')
    return render(request, 'sva/professor/CadastroProfessor.html', {'form': form})


###############################################################################
#                                EMPRESA                                      #
###############################################################################

@transaction.atomic
@login_required(login_url='/accounts/login/')
def editar_empresa(request, pk):

    if pk != str(request.user.id):
        return HttpResponseRedirect('/home/')

    empresa = get_object_or_404(Empresa, user_id=pk)
    Nome = empresa.user.first_name + ' ' + empresa.user.last_name
    if empresa.endereco is not None:
        parte = empresa.endereco.split(",")
        initial = {
            'Nome_Completo': Nome,
            'Telefone': empresa.telefone,
            'Email': empresa.user.email,
            'Site': empresa.website,
            'Bairro': parte[0],
            'Rua': parte[1] if len(parte) >= 2 else '',
            'Numero': parte[2] if len(parte) >= 3 else '',
            'Complemento': parte[3] if len(parte) >= 4 else '',
            'Cidade': parte[4] if len(parte) >= 5 else '',
            'Estado': parte[5] if len(parte) >= 6 else '',
        }
    else:
        initial = {'Nome_Completo': Nome,
            'Telefone': empresa.telefone,
            'Email': empresa.user.email,
            'Site': empresa.website}

    if request.method == 'GET':
        form = FormularioEditarEmpresa(instance=empresa, initial=initial)
    if request.method == 'POST':
        form = FormularioEditarEmpresa(request.POST, instance=empresa, initial=initial)
        if form.is_valid():
            if form.cleaned_data['Site'] is None:
                empresa.website = ""
            else:
                empresa.website = form.cleaned_data['Site']
            if form.cleaned_data['telefone'] is None:
                empresa.telefone = ""
            else:
                empresa.telefone = form.cleaned_data['telefone']
            empresa.nome = form.cleaned_data['nome']
            empresa.endereco = form.cleaned_data['Bairro'] + ',' + \
                               form.cleaned_data['Rua'] + ',' + \
                               form.cleaned_data['Numero'] + ',' + \
                               form.cleaned_data['Complemento'] + ',' + \
                               form.cleaned_data['Cidade'] + ',' + \
                               form.cleaned_data['Estado']
            empresa.save()
            empresa.user.first_name = form.cleaned_data['nome']
            empresa.user.last_name = ""
            empresa.user.email = form.cleaned_data['Email']
            empresa.user.save()
            messages.success(request, 'Editado com sucesso')
            return redirect(exibir_empresa, empresa.user_id)
        else:
            messages.error(request, 'Falha ao editar')
            return redirect(exibir_empresa, empresa.user_id)

    return render(request, 'sva/empresa/EditarEmpresa.html', {'form': form, 'empresa': empresa})


@login_required(login_url='/accounts/login/')
def excluir_empresa(request, pk):
    empresa = get_object_or_404(Empresa, user_id=pk)
    if pk != str(request.user.id):
        messages.error(request, mensagens.ERRO_PERMISSAO_NEGADA, mensagens.MSG_ERRO)
        return HttpResponseRedirect('/home/')
    empresa.user.is_active = False
    empresa.situacao = Empresa.EXCLUIDO
    empresa.save()
    empresa.user.save()
    Vaga.objects.filter(gerente_vaga=empresa).update(situacao=4)  # inativa as vagas
    messages.success(request, mensagens.SUCESSO_ACAO_CONFIRMADA, mensagens.MSG_SUCCESS)
    return HttpResponseRedirect('/home/')


def exibir_empresa(request, pk):
    empresa = get_object_or_404(Empresa, user_id=pk)
    if empresa.endereco is not None:
        parte = empresa.endereco.split(",")
        endereco = {
            'Bairro': parte[0],
            'Rua': parte[1] if len(parte) >= 2 else '',
            'Numero': parte[2] if len(parte) >= 3 else '',
            'Complemento': parte[3] if len(parte) >= 4 else '',
            'Cidade': parte[4] if len(parte) >= 5 else '',
            'Estado': parte[5] if len(parte) >= 6 else '',
        }
    else:
        endereco = {'Bairro': '', 'Rua': '', 'Numero': '', 'Complemento': '', 'Cidade': '', 'Estado': ''}
    context = {'empresa': empresa,
               'endereco': endereco,
               'form_aprovacao': FormularioAprovacao()}
    return render(request, 'sva/empresa/Perfil.html', context)


@login_required(login_url='/accounts/login/')
def listar_empresa(request):
    form = FormularioPesquisaEmpresa(request.POST)
    empresas = Empresa.objects.filter(situacao=Empresa.DEFERIDO)
    if form.is_valid():
        if form.cleaned_data['nome'] is not None and form.cleaned_data['nome'] != "":
            valor = form.cleaned_data['nome']
            query = Empresa.objects.annotate(search_name=Concat('user__first_name', Value(' '), 'user__last_name'))
            empresas = query.filter(Q(situacao=Empresa.DEFERIDO) & Q(nome__icontains=valor))
    context = {
        'titulo_lista': 'Empresas Cadastradas',
        'liberar_cadastro': False,
        'form': form,
        'empresas': empresas
    }
    return render(request, 'sva/empresa/ListarEmpresas.html', context)


@login_required(login_url='/accounts/login/')
@user_passes_test(is_admin)
def liberar_cadastro_empresas_lista(request):
    form = FormularioPesquisaEmpresa(request.POST)
    empresas = Empresa.objects.filter(situacao=Empresa.AGUARDANDO_APROVACAO)
    if form.is_valid():
        if form.cleaned_data['nome'] is not None and form.cleaned_data['nome'] != "":
            valor = form.cleaned_data['nome']
            query = Empresa.objects.annotate(search_name=Concat('user__first_name', Value(' '), 'user__last_name'))
            empresas = query.filter(Q(situacao=Empresa.AGUARDANDO_APROVACAO) & Q(nome__icontains=valor))
    context = {
        'titulo_lista': 'Empresas com Cadastro Pendente',
        'liberar_cadastro': True,
        'form': form,
        'empresas': empresas
    }
    return render(request, 'sva/empresa/ListarEmpresas.html', context)


@transaction.atomic
@login_required
@require_POST
@user_passes_test(is_admin)
def aprovar_cadastro_empresa(request, pk):
    empresa = get_object_or_404(Empresa, user__pk=pk)
    form = FormularioAprovacao(request.POST)
    if empresa is not None and form.is_valid() and form.cleaned_data['aprovado'] == 'true':
        empresa.user.is_active = True
        empresa.user.is_staff = True
        empresa.user.save()
        empresa.data_aprovacao = datetime.now()
        empresa.situacao = Empresa.DEFERIDO
        empresa.save()
        mensagem = 'Seu cadastro no SVA foi aprovado por %s. Segue mensagem:\n\n %s' \
                   'Você agora pode acessar o sistema\n\nSVA' \
                   % (request.user.first_name, request.POST['justificativa'])
        send_mail('Aprovação de Cadastro - Sistema de Vagas Acadêmicas',
                  mensagem, 'sva@cefetmg.br', [empresa.user.email])
    else:
        empresa.situacao = Empresa.INDEFERIDO
        empresa.data_aprovacao = None
        empresa.save()
        mensagem = 'Seu cadastro no SVA foi recusado por %s. Segue mensagem:\n\n%s\n\nSVA' \
                   % (request.user.first_name, request.POST['justificativa'])
        send_mail('Aprovação de Cadastro - Sistema de Vagas Acadêmicas',
                  mensagem, 'sva@cefetmg.br', [empresa.user.email])
    messages.success(request, mensagens.SUCESSO_ACAO_CONFIRMADA, mensagens.MSG_SUCCESS)
    return render(request, 'sva/empresa/Perfil.html', {'empresa': empresa})


###############################################################################
#                                 ALUNO                                       #
###############################################################################

@transaction.atomic
@login_required(login_url='/accounts/login/')
def editar_aluno(request, pk):
    if pk != str(request.user.id):
       return HttpResponseRedirect('/home/')
    aluno = get_object_or_404(Aluno,user_id=pk)
    Parte= aluno.endereco.split(",")
    Nome = aluno.user.first_name+' '+aluno.user.last_name
    initial = {'Rua': Parte[0],
           'Numero': Parte[1] if len(Parte) >= 2 else '',
           'Complemento': Parte[2] if len(Parte) >= 3 else '',
           'Cidade': Parte[3] if len(Parte) >= 4 else '',
           'Estado': Parte[4] if len(Parte) >= 5 else '',
           'Nome_Completo': Nome}
    if request.method == 'POST':
        form = FormularioEditarAluno(request.POST, instance=aluno, initial=initial)
        if form.is_valid():
            aluno.curso = form.cleaned_data['curso']
            aluno.telefone = form.cleaned_data['telefone']
            texto = form.cleaned_data['Nome_Completo']
            Nome = texto.split(" ", 1)
            aluno.endereco = form.cleaned_data['Rua'] + ',' + \
                             form.cleaned_data['Numero'] + ',' +  \
                             form.cleaned_data['Complemento'] + ',' +  \
                             form.cleaned_data['Cidade'] + ',' +  \
                             form.cleaned_data['Estado']
            aluno.save()
            aluno.user.first_name = Nome[0]
            if len(Nome) > 1:
                aluno.user.last_name = Nome[1]
            aluno.habilidades = form.cleaned_data['habilidades']
            aluno.user.save()
            messages.success(request, 'Editado com sucesso')
    else:
        form = FormularioEditarAluno(instance=aluno, initial=initial)
    return render(request, 'sva/aluno/EditarAluno.html', {'form': form})


@login_required(login_url='/accounts/login/')
def excluir_aluno(request, pk):
    aluno = get_object_or_404(Aluno, user_id=pk)
    if pk != str(request.user.id):
        messages.error(request, mensagens.ERRO_PERMISSAO_NEGADA, mensagens.MSG_ERRO)
        return HttpResponseRedirect('/home/')
    if aluno is not None:
        aluno.user.is_active = False
        aluno.user.save()
        messages.success(request, mensagens.SUCESSO_ACAO_CONFIRMADA, mensagens.MSG_SUCCESS)
        return HttpResponseRedirect('/home/')


def exibir_aluno(request, pk):
    aluno = get_object_or_404(Aluno, user_id=pk)
    context = {'aluno': aluno}
    return render(request, 'sva/aluno/Perfil.html', context)


###############################################################################
#                                 ACESSO                                      #
###############################################################################


def layout(request):
    form = FormularioContato()
    return render(request, 'sva/layout.html', {'form': form})


def recuperar_senha(request):
    if request.method == "GET":
        return render(request, 'registration/recuperarSenha.html', {})

    cpf = request.POST['CPF']
    email = request.POST['email']
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        user = None

    if user is not None:
        novasenha = ''.join([choice(string.ascii_letters + string.digits) for i in range(8)])
        send_mail(
            'Recuperação de Senha - Sistema de Vagas Acadêmicas',
            'Sua nova senha é:\n\n' + novasenha + '\n\nPara alterar para uma nova senha de sua preferência,'
                                                  ' acesse sua conta no site sva.cefetmg.br e vá na pagina'
                                                  ' de configurações do Usuário\n\nSVA',
            'from@example.com',
            [email],
        )
        user.set_password(novasenha)
        user.save()
        messages.success(request, _('Sua nova senha foi enviado para o email a sua conta!'))
        return redirect('login')
    else:
        messages.error(request, mensagens.ERRO_EMAIL_INVALIDO, mensagens.MSG_ERRO)
        return render(request, 'registration/recuperarSenha.html', {})


def alterar_senha(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, _('Sua senha foi alterada com sucesso!'))
            return redirect('home')
        else:
            messages.error(request, _('Por favor, corrija os erros abaixo'))
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/alterar_senha.html', {
        'form': form
    })


###############################################################################
#                               PROFESSOR                                     #
###############################################################################


@transaction.atomic
@login_required(login_url='/accounts/login/')
def editar_professor(request, pk):
    professor = get_object_or_404(Professor, user__pk=pk)
    Nome = professor.user.first_name + ' ' + professor.user.last_name
    Telefone = professor.telefone
    Curso = professor.curso
    initial = {
        'Nome_Completo': Nome,
        'Telefone': Telefone,
        'Curso': Curso}

    if request.method == 'POST':
        form = FormularioEditarProfessor(request.POST, instance=professor, initial=initial)
        if form.is_valid():
            texto = form.cleaned_data['Nome_Completo']
            Nome = texto.split(" ", 1)
            professor.curso = form.cleaned_data['curso']
            professor.siape = form.cleaned_data['siape']
            professor.telefone = form.cleaned_data['Telefone']
            professor.save()
            professor.user.first_name = Nome[0] if len(Nome) > 0 else ''
            professor.user.last_name = Nome[1] if len(Nome) > 1 else ''
            professor.user.save()
            messages.success(request, 'Editado com sucesso!')
            return redirect(exibir_professor, professor.user.id)
    else:
        form = FormularioEditarProfessor(instance=professor, initial=initial)
    return render(request, 'sva/professor/EditarProfessor.html', {'form': form, 'professor': professor})


@transaction.atomic
@login_required(login_url='/accounts/login/')
def excluir_professor(request, pk):
    professor = get_object_or_404(Professor, user__pk=pk)
    if pk != str(request.user.id):
        messages.error(request, mensagens.ERRO_PERMISSAO_NEGADA, mensagens.MSG_ERRO)
        return HttpResponseRedirect('/home/')
    professor.user.is_active = False
    professor.situacao = Professor.EXCLUIDO
    Vaga.objects.filter(gerente_vaga=professor).update(situacao=4)  # inativa as vagas
    professor.user.save()
    professor.save()
    messages.error(request, mensagens.SUCESSO_ACAO_CONFIRMADA, mensagens.MSG_SUCCESS)
    return HttpResponseRedirect('/home/')


@login_required(login_url="/home/")
def Listar_Vagas_Aluno(request, pk):
    aluno = get_object_or_404(Aluno, user_id=pk)
    if pk != str(request.user.id):
        messages.error(request, mensagens.ERRO_PERMISSAO_NEGADA, mensagens.MSG_ERRO)
        return HttpResponseRedirect('/home/')
    form = FormularioPesquisaVagasAluno(request.POST)
    context = {}
    context['form']=form
    if form.is_valid():
            if form.cleaned_data['Area_Atuacao']=="":
                context['vagas_inscritas'] = Vaga.objects.filter(alunos_inscritos=aluno,titulo__icontains= form.cleaned_data['Vaga_Cadastrada'])
                context['vagas_interesse'] = Vaga.objects.filter(alunos_interessados=aluno,titulo__icontains=form.cleaned_data['Vaga_Cadastrada'])
            elif form.cleaned_data['Vaga_Cadastrada']=="":
                areas=AreaAtuacao.objects.filter(nome__icontains= form.cleaned_data['Area_Atuacao'])
                for area in areas:
                    context['vagas_inscritas'] = Vaga.objects.filter(alunos_inscritos=aluno, areas_atuacao=area.id)
                    context['vagas_interesse'] = Vaga.objects.filter(alunos_interessados=aluno, areas_atuacao=area.id)
            else:
                areas = AreaAtuacao.objects.filter(nome__icontains=form.cleaned_data['Area_Atuacao'])
                for area in areas:
                    context['vagas_inscritas'] = Vaga.objects.filter(alunos_inscritos=aluno,titulo__icontains= form.cleaned_data['Vaga_Cadastrada'], areas_atuacao=area.id)
                    context['vagas_interesse'] = Vaga.objects.filter(alunos_interessados=aluno,titulo__icontains= form.cleaned_data['Vaga_Cadastrada'], areas_atuacao=area.id)
    else:
        context['vagas'] = Vaga.objects.filter(alunos_inscritos=aluno)
    context['now']= timezone.now()
    return render(request, 'sva/aluno/Vagas.html', context)


@login_required(login_url='/accounts/login/')
def exibir_professor(request, pk):
    professor = get_object_or_404(Professor, user_id=pk)
    context = {'professor': professor,
               'form_aprovacao': FormularioAprovacao()}
    return render(request, 'sva/professor/Perfil.html', context)


@login_required(login_url='/accounts/login/')
def listar_professor(request):
    form = FormularioPesquisaProfessor(request.POST)
    professores = professores = Professor.objects.filter(situacao=Professor.DEFERIDO)
    if form.is_valid():
        if form.cleaned_data['curso_campus_nome'] is not None and form.cleaned_data['curso_campus_nome'] != "":
            valor = form.cleaned_data['curso_campus_nome']
            query = Professor.objects.annotate(search_name=Concat('user__first_name', Value(' '), 'user__last_name'))
            professores = query.filter(Q(situacao=Professor.DEFERIDO) & (
                                           Q(search_name__icontains=valor) |
                                           Q(curso__nome__icontains=valor) |
                                           Q(curso__campus__nome__icontains=valor)))
    context = {
        'titulo_lista': 'Professores Cadastrados',
        'liberar_cadastro': False,
        'form': form,
        'professores': professores,
        'people': ProfessorTable(),
    }
    return render(request, 'sva/professor/ListarProfessores.html', context)


@login_required(login_url='/accounts/login/')
@user_passes_test(is_admin)
def liberar_cadastro_professores_lista(request):
    form = FormularioPesquisaProfessor(request.POST)
    professores = Professor.objects.filter(situacao=Professor.AGUARDANDO_APROVACAO)
    if form.is_valid():
        if form.cleaned_data['curso_campus_nome'] is not None and form.cleaned_data['curso_campus_nome'] != "":
            valor = form.cleaned_data['curso_campus_nome']
            query = Professor.objects.annotate(search_name=Concat('user__first_name', Value(' '), 'user__last_name'))
            professores = query.filter(Q(situacao=Professor.AGUARDANDO_APROVACAO) & (
                    Q(search_name__icontains=valor) |
                    Q(curso__nome__icontains=valor) |
                    Q(curso__campus__nome__icontains=valor)))
    context = {
        'titulo_lista': 'Professores com Cadastro Pendente',
        'liberar_cadastro': True,
        'form': form,
        'professores': professores,
        'people': ProfessorTable(),
    }
    return render(request, 'sva/professor/ListarProfessores.html', context)


@transaction.atomic
@login_required
@require_POST
@user_passes_test(is_admin)
def aprovar_cadastro_professor(request, pk):
    professor = get_object_or_404(Professor, user__pk=pk)
    form = FormularioAprovacao(request.POST)
    if professor is not None and form.is_valid() and form.cleaned_data['aprovado'] == 'true':
        professor.user.is_active = True
        professor.user.is_staff = True
        professor.user.save()
        professor.data_aprovacao = datetime.now()
        professor.situacao = Professor.DEFERIDO
        professor.save()
        mensagem = 'Seu cadastro no SVA foi aprovado por %s. Segue mensagem:\n\n %s' \
                   'Você agora pode acessar o sistema\n\nSVA' \
                   % (request.user.first_name, form.cleaned_data['justificativa'])
        send_mail('Aprovação de Cadastro - Sistema de Vagas Acadêmicas',
                  mensagem, 'sva@cefetmg.br', [professor.user.email])
    else:
        professor.situacao = Professor.INDEFERIDO
        professor.data_aprovacao = None
        professor.save()
        mensagem = 'Seu cadastro no SVA foi recusado por %s. Segue mensagem:\n\n%s\n\nSVA' \
                   % (request.user.first_name, form.cleaned_data['justificativa'])
        send_mail('Recusa de Cadastro - Sistema de Vagas Acadêmicas',
                  mensagem, 'sva@cefetmg.br', [professor.user.email])
    messages.success(request, mensagens.SUCESSO_ACAO_CONFIRMADA, mensagens.MSG_SUCCESS)
    return render(request, 'sva/professor/Perfil.html', {'professor': professor})

