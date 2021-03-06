# -*- coding: utf-8 -*-
from operator import attrgetter
from typing import Dict, Any, Union, ContextManager

from django.urls import reverse
from django.contrib import messages
from django.db.models.functions import Concat
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.db import transaction
from django.db.models import Q, Value, Count
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.template import RequestContext
from django.core import serializers
import string
from random import choice
import json

from django.views.decorators.http import require_POST

from sva import mensagens
from .models import *
from .forms import *
from datetime import datetime


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

    def verificaAreasAtuacao(vaga, nome_area):
        areas_vaga = AreaAtuacao.objects.filter(vagas=vaga)
        for area in areas_vaga:
            if nome_area in area.nome:
                return True
        return False

    def verificaAreasAtuacaoByID(vaga, id_area):
        try:
            AreaAtuacao.objects.get(vagas=vaga, id=id_area)
            return True
        except:
            return False

    def verificaCursos(vaga, nome_curso):
        cursos_vaga = Curso.objects.filter(vagas_atribuidas=vaga)
        for curso in cursos_vaga:
            if nome_curso in curso.nome or nome_curso in curso.sigla:
                #nome_curso in curso.get_nivel_ensino_display()
                return True
        return False

    def verificaCursoByID(vaga, id_curso):
        try:
            Curso.objects.get(vagas_atribuidas=vaga, id=id_curso)
            return True
        except:
            if Curso.objects.filter(vagas_atribuidas=vaga).count() == 0: #OFERTADA A TODOS OS CURSOS
                return True
            else:
                return False

    def verificaCursoByNivel(vaga, nivel_ensino):
        if Curso.objects.filter(vagas_atribuidas=vaga).count() == 0: #OFERTADA A TODOS OS CURSOS
            return True
        cursos_vaga = Curso.objects.filter(vagas_atribuidas=vaga)
        for curso in cursos_vaga:
            if nivel_ensino == curso.nivel_ensino:
                return True
        return False

    #Formulario base de pesquisa (trata querysets de area e curso somente, os outros campos sao colocados via template)
    form = FormularioPesquisarVagas(request.POST)
    #Armazena palavras chave pesquisadas
    busca = []
    #FORCA POST_INIT SIGNAL PARA ATUALIZAR SITUACAO DE VAGAS VENCIDAS
    updatedVaga = Vaga.objects.filter().first()

    #LISTA INICIAL DE OBJETOS DA PESQUISA
    vagas = Vaga.objects.filter(situacao=Vaga.ATIVA)

    #Form initial value
    initial = ""
    try:
        alunoRadio = Aluno.objects.get(user=request.user)
        if alunoRadio.curso.nivel_ensino == 1:
            radioInitial = 1
        elif alunoRadio.curso.nivel_ensino == 2:
            radioInitial = 2
        elif alunoRadio.curso.nivel_ensino == 3:
            radioInitial = 3
        elif alunoRadio.curso.nivel_ensino == 4:
            radioInitial = 4
        elif alunoRadio.curso.nivel_ensino == 5:
            radioInitial = 5
        else:
            radioInitial = 1
        if request.method != 'POST':
            vagasAux = []
            for vaga in vagas:
                radioInitialFlag = True
                if radioInitial == 1 and not verificaCursoByNivel(vaga, 1):
                    radioInitialFlag = False
                if radioInitial == 2 and not verificaCursoByNivel(vaga, 2):
                    radioInitialFlag = False
                if radioInitial == 3 and not verificaCursoByNivel(vaga, 3):
                    radioInitialFlag = False
                if radioInitial == 4 and not verificaCursoByNivel(vaga, 4):
                    radioInitialFlag = False
                if radioInitial == 5 and not verificaCursoByNivel(vaga, 5):
                    radioInitialFlag = False
                if radioInitialFlag == True:
                    vagasAux.append(vaga)
            vagas = vagasAux
    except:
        radioInitial = 0

    formRemake = False
    ordemRemake = 0
    superuserOptionRemake = 0
    salarioRemake = None
    minvalueRemake = 5
    maxvalueRemake = 45
    checkBoxRemake = []
    radioRemake = radioInitial
    avaliacaoRemake = 0
    filtroRemake = []
    textoRemake = []
    areaRemake = []
    cursoRemake = []
    filtrosPesquisa = []
    if request.user.is_authenticated():
        filtrosPesquisa = FiltroPesquisa.objects.filter(user=request.user)

    # DELETA FILTRO
    if request.method == 'POST' and request.POST['type'] == "remove_filter":
        filtroPesquisaRemove = FiltroPesquisa.objects.get(id=int(request.POST['filtro_remover']))
        filtroNomeRemove = filtroPesquisaRemove.nome
        Filtro.objects.filter(pesquisa=filtroPesquisaRemove).delete()
        filtroPesquisaRemove.filtros.clear()
        filtroPesquisaRemove.delete()
        messages.success(request, 'Filtro de pesquisa %s deletado com sucesso' % filtroNomeRemove, mensagens.MSG_SUCCESS)


    #SALVAR FILTRO
    if request.method == 'POST' and request.POST['type']=="add_filter":
        nome_filtro = request.POST['novo_filtro']
        if request.user.is_authenticated() and request.POST['novo_filtro'] is not None and request.POST['novo_filtro'] != "":
            countFiltros = FiltroPesquisa.objects.filter(user=request.user).count()
            if countFiltros == 5:
                messages.error(request, mensagens.ERRO_QUANT_MAX_FILTROS, mensagens.MSG_ERRO)
            elif FiltroPesquisa.objects.filter(user=request.user, nome=request.POST['novo_filtro']).count() > 0:
                messages.error(request, 'Um filtro com o nome %s já existe' % request.POST['novo_filtro'], mensagens.MSG_ERRO)
            else:
                novoFiltroPesquisa = FiltroPesquisa()
                novoFiltroPesquisa.user = request.user
                novoFiltroPesquisa.nome = nome_filtro
                novoFiltroPesquisa.ordenacao = int(request.POST.get('ordem'))
                if not is_admin(request.user):
                    novoFiltroPesquisa.situacao = FiltroPesquisa.ATIVAS
                else:
                    novoFiltroPesquisa.situacao = int(request.POST.get('superuser_option'))
                if request.POST.get('estagio') == "on":
                    novoFiltroPesquisa.tipo_estagio = True
                else:
                    novoFiltroPesquisa.tipo_estagio = False
                if request.POST.get('monitoria') == "on":
                    novoFiltroPesquisa.tipo_monitoria = True
                else:
                    novoFiltroPesquisa.tipo_monitoria = False
                if request.POST.get('ic') == "on":
                    novoFiltroPesquisa.tipo_ic = True
                else:
                    novoFiltroPesquisa.tipo_ic = False
                if request.POST.get('outros') == "on":
                    novoFiltroPesquisa.tipo_outros = True
                else:
                    novoFiltroPesquisa.tipo_outros = False
                if request.POST.get('radioNivel') is not None:
                    novoFiltroPesquisa.nivel = int(request.POST.get('radioNivel'))
                else:
                    novoFiltroPesquisa.nivel = FiltroPesquisa.NENHUM_SELECIONADO
                novoFiltroPesquisa.carga_horaria_minima = int(request.POST.get('min-value'))
                novoFiltroPesquisa.carga_horaria_maxima = int(request.POST.get('max-value'))
                if request.POST.get('salario') is not None and request.POST.get('salario') != "":
                    novoFiltroPesquisa.salario = float(request.POST.get('salario'))
                else:
                    novoFiltroPesquisa.salario = 0
                novoFiltroPesquisa.avaliacao = int(request.POST.get('avaliacao'))
                filtros = request.POST.getlist('filtro')
                textoFiltro = request.POST.getlist('texto')
                cursoFiltro = request.POST.getlist('curso')
                areaFiltro = request.POST.getlist('area')
                aux = 0
                filtrosAuxList = []
                errorOnLoop = False
                for filtro in filtros:
                    novoFiltro = Filtro()
                    novoFiltro.tipo = int(filtro)
                    if textoFiltro[aux] == "" or textoFiltro[aux] is None:
                        novoFiltro.texto = ""
                    else:
                        novoFiltro.texto = textoFiltro[aux]
                    try:
                        area = AreaAtuacao.objects.get(id=int(areaFiltro[aux]))
                        novoFiltro.areas_atuacao = area
                        curso = Curso.objects.get(id=int(cursoFiltro[aux]))
                        novoFiltro.cursos = curso
                        novoFiltro.save()
                        filtrosAuxList.append(novoFiltro)
                    except:
                        errorOnLoop = True
                        continue
                    aux+=1
                if errorOnLoop is True:
                    for filtro in filtrosAuxList:
                        filtro.delete()
                    messages.error(request, mensagens.ERRO_PROCESSAMENTO, mensagens.MSG_ERRO)
                else:
                    novoFiltroPesquisa.save()
                for filtro in filtrosAuxList:
                    novoFiltroPesquisa.filtros.add(filtro)
                messages.success(request, 'Filtro de pesquisa %s criado com sucesso' % nome_filtro, mensagens.MSG_SUCCESS)

    if request.method == 'POST' and form.is_valid():
        if request.POST['type'] == "load_filter":
            filtroPesquisaLoad = FiltroPesquisa.objects.get(user=request.user, id=int(request.POST['filtro_carregar']))
            formRemake = True
            ordemRemake = str(filtroPesquisaLoad.ordenacao)
            superuserOptionRemake = str(filtroPesquisaLoad.situacao)
            checkBoxRemake.append("on") if filtroPesquisaLoad.tipo_estagio is True else checkBoxRemake.append("off")
            checkBoxRemake.append("on") if filtroPesquisaLoad.tipo_monitoria is True else checkBoxRemake.append("off")
            checkBoxRemake.append("on") if filtroPesquisaLoad.tipo_ic is True else checkBoxRemake.append("off")
            checkBoxRemake.append("on") if filtroPesquisaLoad.tipo_outros is True else checkBoxRemake.append("off")
            radioRemake = filtroPesquisaLoad.nivel
            salarioRemake = str(filtroPesquisaLoad.salario)
            minvalueRemake = filtroPesquisaLoad.carga_horaria_minima
            maxvalueRemake = filtroPesquisaLoad.carga_horaria_maxima
            avaliacaoRemake = str(filtroPesquisaLoad.avaliacao)
            filtroLoad = Filtro.objects.filter(pesquisa=filtroPesquisaLoad)
            for filtro in filtroLoad:
                filtroRemake.append(str(filtro.tipo))
                textoRemake.append(filtro.texto) if filtro.texto is not None and filtro.texto != "" else textoRemake.append("")
                cursoRemake.append(filtro.cursos.id)
                areaRemake.append(filtro.areas_atuacao.id)

        else:
            formRemake = True
            ordemRemake = request.POST.get('ordem')
            superuserOptionRemake = request.POST.get('superuser_option')
            checkBoxRemake.append("on") if request.POST.get('estagio') == "on" else checkBoxRemake.append("off")
            checkBoxRemake.append("on") if request.POST.get('monitoria') == "on" else checkBoxRemake.append("off")
            checkBoxRemake.append("on") if request.POST.get('ic') == "on" else checkBoxRemake.append("off")
            checkBoxRemake.append("on") if request.POST.get('outros') == "on" else checkBoxRemake.append("off")
            radioRemake = int(request.POST.get('radioNivel')) if request.POST.get('radioNivel') is not None else 0
            salarioRemake = request.POST.get('salario')
            minvalueRemake = request.POST.get('min-value')
            maxvalueRemake = request.POST.get('max-value')
            avaliacaoRemake = request.POST.get('avaliacao')

            aux=0
            filtroSelecionado = request.POST.getlist('filtro')
            inputTexto = request.POST.getlist('texto')
            inputCurso = request.POST.getlist('curso')
            inputArea = request.POST.getlist('area')
            for filtro in filtroSelecionado:
                filtroRemake.append(filtro)
                textoRemake.append(inputTexto[aux]) if inputTexto[aux] is not None and inputTexto[aux] != "" else textoRemake.append("")
                cursoRemake.append(int(inputCurso[aux]))
                areaRemake.append(int(inputArea[aux]))
                aux+=1

        ordem_resultados = ordemRemake
        if is_admin(request.user):
            # ORDENA POR VAGAS MAIS RECENTES
            if ordem_resultados == "1":
                vagas = Vaga.objects.filter().order_by('-data_submissao')
            # ORDENA POR DATA DE SUBMISSAO
            elif ordem_resultados == "2":
                vagas = Vaga.objects.filter().annotate(num_insc=Count('alunos_inscritos')).order_by(
                    '-num_insc')
            # ORDENA POR AVALIACOES
            elif ordem_resultados == "3":
                vagas = Vaga.objects.filter().order_by('-nota_media')
            # ORDENA POR MAIS COMENTADAS
            elif ordem_resultados == "4":
                vagas = Vaga.objects.filter(situacao=Vaga.ATIVA).annotate(num_comentarios=Count('comentario')).order_by('-num_comentarios')
            # ORDENA POR MENOR PRAZO
            elif ordem_resultados == "5":
                vagas = Vaga.objects.filter().order_by('data_validade')
            # ORDENACAO PADRAO (NAO ENTRA NOS CASOS DO SELECT)
            else:
                vagas = Vaga.objects.filter()

            #TRATA SELECAO ESPECIAL DO SUPER USUARIO POR SITUACAO DA VAGA
            superuser_option = superuserOptionRemake
            vagasAux = []
            for vaga in vagas:
                if superuser_option == "1" and vaga.situacao == Vaga.ATIVA:
                    vagasAux.append(vaga)
                if (vaga.situacao == Vaga.CADASTRADA or vaga.situacao == Vaga.EDITADA) and superuser_option == "2":
                    vagasAux.append(vaga)
                if superuser_option == "3" and vaga.situacao == Vaga.INATIVA:
                    vagasAux.append(vaga)
                if superuser_option == "4" and vaga.situacao == Vaga.REPROVADA:
                    vagasAux.append(vaga)
                if superuser_option == "5":
                    vagasAux = vagas
                    break
            vagas = vagasAux
        else:
            # ORDENA POR VAGAS MAIS RECENTES
            if ordem_resultados == "1":
                vagas = Vaga.objects.filter(situacao=Vaga.ATIVA).order_by('-data_submissao')
            # ORDENA POR DATA DE SUBMISSAO
            elif ordem_resultados == "2":
                vagas = Vaga.objects.filter(situacao=Vaga.ATIVA).annotate(num_insc=Count('alunos_inscritos')).order_by('-num_insc')
            # ORDENA POR AVALIACOES
            elif ordem_resultados == "3":
                vagas = Vaga.objects.filter(situacao=Vaga.ATIVA).order_by('-nota_media')
            # ORDENA POR MAIS COMENTADAS
            elif ordem_resultados == "4":
                vagas = Vaga.objects.filter(situacao=Vaga.ATIVA).annotate(num_comentarios=Count('comentario')).order_by('-num_comentarios')
            # ORDENA POR MENOR PRAZO
            elif ordem_resultados == "5":
                vagas = Vaga.objects.filter(situacao=Vaga.ATIVA).order_by('data_validade')
            # ORDENACAO PADRAO (NAO ENTRA NOS CASOS DO SELECT)
            else:
                vagas = Vaga.objects.filter(situacao=Vaga.ATIVA)

        vagasAux = []
        #TRATA FILTROS CHECKBOX
        for vaga in vagas:
            addFlag = False
            if checkBoxRemake[0] == "on" and vaga.tipo_vaga == 1:
                addFlag = True
            elif checkBoxRemake[1] == "on" and vaga.tipo_vaga == 2:
                addFlag = True
            elif checkBoxRemake[2] == "on" and vaga.tipo_vaga == 3:
                addFlag = True
            elif checkBoxRemake[3] == "on" and vaga.tipo_vaga == 4:
                addFlag = True
            if radioRemake == 1 and not verificaCursoByNivel(vaga, 1):
                addFlag = False
            if radioRemake == 2 and not verificaCursoByNivel(vaga, 2):
                addFlag = False
            if radioRemake == 3and not verificaCursoByNivel(vaga, 3):
                addFlag = False
            if radioRemake == 4 and not verificaCursoByNivel(vaga, 4):
                addFlag = False
            if radioRemake == 5 and not verificaCursoByNivel(vaga, 5):
                addFlag = False
            if addFlag == True:
                vagasAux.append(vaga)

        vagas = vagasAux

        vagasAux = []
        #TRATA FILTRO VALORES E SLIDERS
        for vaga in vagas:
            if salarioRemake is not None and salarioRemake != "":
                if vaga.valor_bolsa >= float(salarioRemake) and vaga.carga_horaria_semanal >= int(minvalueRemake) \
                        and vaga.carga_horaria_semanal <= int(maxvalueRemake) and vaga.nota_media >= int(avaliacaoRemake):
                    vagasAux.append(vaga)
                    continue
            elif vaga.carga_horaria_semanal >= int(minvalueRemake) and vaga.carga_horaria_semanal <= int(maxvalueRemake) and vaga.nota_media >= int(avaliacaoRemake):
                vagasAux.append(vaga)
        vagas = vagasAux

        #Listas auxiliares para tratar os dados em lista do request.post
        filtroSelecionado = filtroRemake
        inputTexto = textoRemake
        inputCurso = cursoRemake
        inputArea = areaRemake
        aux = 0
        for filtro in filtroSelecionado:
            #Lista auxiliar de vagas filtradas para lista de resposta da solicitação
            vagasAux = []
            #FILTRO - TODOS OS CAMPOS
            #VERIFICA SE O INPUT DE TEXTO TEM CASAMENTO EM QUALQUER UM DOS CAMPOS: Nome do gerente de vagas, areas de atuacao, cursos, titulo, descricao, local ou beneficios da vaga.
            if filtro == "1":
                if inputTexto[aux] is not None and inputTexto[aux] != "":
                    busca.append(inputTexto[aux])
                    for vaga in vagas:
                        if inputTexto[aux] in vaga.gerente_vaga.user.first_name or inputTexto[aux] in vaga.gerente_vaga.user.last_name:
                            vagasAux.append(vaga)
                            continue
                        if verificaAreasAtuacao(vaga, inputTexto[aux]):
                            vagasAux.append(vaga)
                            continue
                        if verificaCursos(vaga, inputTexto[aux]):
                            vagasAux.append(vaga)
                            continue
                        if inputTexto[aux] in vaga.titulo:
                            vagasAux.append(vaga)
                            continue
                        if inputTexto[aux] in vaga.descricao:
                            vagasAux.append(vaga)
                            continue
                        if vaga.gerente_vaga.user.groups.filter(name__in=['Empresa']).exists():
                            if inputTexto[aux] in vaga.local or inputTexto[aux] in vaga.gerente_vaga.empresa.endereco:
                                vagasAux.append(vaga)
                                continue
                        else:
                            if inputTexto[aux] in vaga.local:
                                vagasAux.append(vaga)
                                continue
                        if inputTexto[aux] in vaga.local:
                            vagasAux.append(vaga)
                            continue
                        if inputTexto[aux] in vaga.beneficios:
                            vagasAux.append(vaga)
                            continue
                    vagas = vagasAux
            #FILTRO - NOME DE VAGAS
            #VERIFICA SE O INPUT DE TEXTO TEM CASAMENTO COM O TITULO DA VAGA
            elif filtro == "2":
                if inputTexto[aux] is not None and inputTexto[aux] != "":
                    busca.append(inputTexto[aux])
                    for vaga in vagas:
                        if inputTexto[aux] in vaga.titulo:
                            vagasAux.append(vaga)
                    vagas = vagasAux
            #FILTRO - EMPRESAS E/OU PROFESSORES
            #VERIFICA SE O INPUT DE TEXTO TEM CASAMENTO COM O NOME DO GERENTE DE VAGA
            elif filtro == "3":
                if inputTexto[aux] is not None and inputTexto[aux] != "":
                    busca.append(inputTexto[aux])
                    for vaga in vagas:
                        if inputTexto[aux] in vaga.gerente_vaga.user.first_name or inputTexto[aux] in vaga.gerente_vaga.user.last_name:
                            vagasAux.append(vaga)
                    vagas = vagasAux
            #FILTRO - AREAS DE ATUACAO
            #VERIFICA SE O SELECT DE AREAS DE ATUACAO (RETORNA ID) TEM CASAMENTO COM O ID DE PELO MENOS UMA AREA DE ATUACAO DA VAGA
            elif filtro == "4":
                area = AreaAtuacao.objects.get(id=inputArea[aux])
                busca.append(area.nome)
                for vaga in vagas:
                    if verificaAreasAtuacaoByID(vaga, inputArea[aux]):
                        vagasAux.append(vaga)
                vagas = vagasAux
            #FILTRO - CURSOS
            #VERIFICA SE O SELECT DE CURSOS (RETORNA ID) TEM CASAMENTO COM O ID DE PELO MENOS UM CURSO DA VAGA (SE A VAGA NAO TIVER CURSO, ELA EH CONSIDERADA DISPONIVEL PARA TODOS)
            elif filtro == "5":
                curso = Curso.objects.get(id=inputCurso[aux])
                busca.append(curso.nome)
                for vaga in vagas:
                    if verificaCursoByID(vaga, inputCurso[aux]):
                        vagasAux.append(vaga)
                vagas = vagasAux
            #FILTRO - DESCRICAO
            #VERIFICA SE O INPUT DE TEXTO TEM CASAMENTO COM A DESCRICAO OU OS BENEFICIOS DA VAGA
            elif filtro == "6":
                if inputTexto[aux] is not None and inputTexto[aux] != "":
                    busca.append(inputTexto[aux])
                    for vaga in vagas:
                        if inputTexto[aux] in vaga.descricao or inputTexto[aux] in vaga.beneficios:
                            vagasAux.append(vaga)
                    vagas = vagasAux
            #FILTRO - LOCAL
            #VERIFICA SE O INPUT DE TEXTO TEM CASAMENTO COM O LOCAL DA VAGA OU LOCAL DA EMPRESA
            elif filtro == "7":
                if inputTexto[aux] is not None and inputTexto[aux] != "":
                    busca.append(inputTexto[aux])
                    for vaga in vagas:
                        if vaga.gerente_vaga.user.groups.filter(name__in=['Empresa']).exists():
                            if inputTexto[aux] in vaga.local or inputTexto[aux] in vaga.gerente_vaga.empresa.endereco:
                                vagasAux.append(vaga)
                        else:
                            if inputTexto[aux] in vaga.local:
                                vagasAux.append(vaga)
                    vagas = vagasAux
            #FILTRO - NENHUM CASO ATENDIDO
            else:
                vagasAux = Vaga.objects.filter(situacao=Vaga.ATIVA)
                vagas = vagasAux
            #Incrementa auxiliar iterador da lista
            aux+=1

    if request.method == 'POST':
        # Se a busca vier do "Pesquisa rápida", será tratado nesse trecho
        if 'buscar_keyword' in request.POST and request.POST.get('buscar_keyword') is not None and request.POST.get(
                'buscar_keyword') != '':
            vagas = Vaga.objects.filter(situacao=Vaga.ATIVA)
            busca_rapida = request.POST.get('buscar_keyword')
            vagas = vagas.filter(titulo__icontains=busca_rapida)
            busca.append(request.POST.get('buscar_keyword'))
            initial = busca_rapida

    busca = ', '.join(busca)
    context = {'now': datetime.now(), 'form': form, 'vagas': vagas, 'busca': busca, 'initial': initial,
               'formRemake': formRemake, 'ordemRemake': ordemRemake, 'checkBoxRemake': checkBoxRemake, 'salarioRemake': salarioRemake, 'minvalueRemake': minvalueRemake, 'maxvalueRemake': maxvalueRemake,
               'avaliacaoRemake': avaliacaoRemake, 'superuserOptionRemake': superuserOptionRemake, 'radioRemake': radioRemake, 'filtroRemake': filtroRemake, 'textoRemake': textoRemake, 'areaRemake': areaRemake,
               'cursoRemake': cursoRemake, 'cursosChoices': Curso.objects.all(), 'areasChoices': AreaAtuacao.objects.all(), 'filtrosPesquisa': filtrosPesquisa}
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

@csrf_exempt
@login_required
@transaction.atomic
@user_passes_test(isGerenteVaga, login_url="/home/")
def criar_vaga(request):
    gerente = GerenteVaga.objects.get(user=request.user)
    if gerente is None or gerente.situacao != "DEFERIDO":
        messages.error(request, mensagens.ERRO_GERENTE_INATIVO, mensagens.MSG_ERRO)
        return redirect(principal_vaga)
    if request.is_ajax():
        novaarea = AreaAtuacao()
        if AreaAtuacao.objects.filter(nome=request.POST['area']).first():
            return redirect(gerenciar_areaatuacao)
        novaarea.nome = request.POST['area']
        print ("Nova area"+request.POST['area'])
        novaarea.situacao = AreaAtuacao.AGUARDANDO_APROVACAO
        novaarea.save()

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
    context = {'form': form, 'gerente': gerente}
    return render(request, 'sva/vaga/criarVaga.html', context)


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
    form = IndicarVaga(request.POST)
    vaga = get_object_or_404(Vaga, id=pkvaga)
    context['comentarios'] = Comentario.objects.filter(vaga=vaga)
    context['vaga'] = vaga
    context['form'] = form
    gerente = GerenteVaga.objects.get(vagas=vaga)
    aluno_inscrito_exists = False
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
            aluno_inscrito_exists = True
            context['inscrito'] = 1
            context['interessado'] = 2
        else:
            context['inscrito'] = 0

    context['gerente'] = gerente
    if request.user != gerente.user and vaga.situacao != 3 and not is_admin(request.user) and not aluno_inscrito_exists:
        messages.error(request, mensagens.ERRO_PERMISSAO_NEGADA, mensagens.MSG_ERRO)
        return redirect(principal_vaga)

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
        elif 'indicar' in request.POST:
            if form.is_valid():
                    try:
                        notifica = Notificacao()
                        notifica.tipo = 1
                        notifica.mensagem = aluno.user.first_name + ' indicou uma vaga para você. Clique para visualizar'
                        notifica.link = reverse("vaga_visualizar", args={pkvaga})
                        notifica.usuario = User.objects.get(email=form.cleaned_data['email'])
                        try:
                            Aluno.objects.get(user=notifica.usuario)
                        except:
                            messages.error(request, 'O email indicado é de um usuário do sistema que não tem permissão para ser indicado')
                            return redirect(visualizar_vaga, vaga.id)
                        notifica.vaga = vaga
                        notifica.save()
                        mensagem = aluno.user.first_name+ ' indicou uma vaga para você. \n\n Descrição:\n\n ' \
                                   +vaga.descricao
                        send_mail('Vaga indicada - Sistema de Vagas Acadêmicas',
                                  mensagem, 'sva@cefetmg.br', [form.cleaned_data['email']])
                    except:
                        mensagem = aluno.user.first_name + 'indicou uma vaga para você. \n\n Descrição:\n\n' \
                                   + vaga.descricao
                        send_mail('Vaga indicada - Sistema de Vagas Acadêmicas',
                                  mensagem, 'sva@cefetmg.br', [form.cleaned_data['email']])
                    messages.success(request, 'Indicado com sucesso')
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
        if vaga.data_validade is not None:
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

    vaga = get_object_or_404(Vaga, id=pkvaga)
    form = FormularioAprovacao(request.POST)
    if vaga is not None and form.is_valid() and form.cleaned_data['aprovado'] == 'true':
        vaga.situacao = Vaga.ATIVA
        vaga.data_aprovacao = datetime.now()
        vaga.usuario_aprovacao = request.user
        vaga.save()
        mensagem = 'Seu cadastro da vaga %s foi aprovado no SVA por %s. Segue mensagem:\n\n %s' \
                   % (vaga.titulo, request.user.first_name, form.cleaned_data['justificativa'])
        send_mail('Avaliação de cadastro de vaga - Sistema de Vagas Acadêmicas',
                  mensagem, 'sva@cefetmg.br', [vaga.gerente_vaga.user.email])
    else:
        vaga.situacao = Vaga.REPROVADA
        vaga.descricao = form.cleaned_data['justificativa'].upper() + '\n\n' + vaga.descricao
        vaga.save()
        mensagem = 'Seu cadastro da vaga %s foi recusado no SVA por %s. Segue mensagem:\n\n%s\n\nSVA' \
                   % (vaga.titulo, request.user.first_name, form.cleaned_data['justificativa'])
        send_mail('Avaliação de cadastro de vaga - Sistema de Vagas Acadêmicas',
                  mensagem, 'sva@cefetmg.br', [vaga.gerente_vaga.user.email])
    messages.success(request, mensagens.SUCESSO_ACAO_CONFIRMADA, mensagens.MSG_SUCCESS)

    return redirect(visualizar_vaga, pkvaga)

@login_required(login_url='/accounts/login/')
def adicionar_comentario(request,pkvaga):
    vaga = get_object_or_404(Vaga, pk=pkvaga)
    comentario = Comentario()
    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.get(id=form.cleaned_data['resposta'])
                realname = user.first_name+" "+user.last_name
                parte1 = form.cleaned_data['text'].split("[")
                string = parte1[1].split("]")
                comentario.user = request.user
                comentario.vaga = vaga
                comentario.text = form.cleaned_data['text']
                comentario.save()
                if string[0] == realname:
                    notifica = Notificacao()
                    notifica.tipo = 9
                    notifica.mensagem = request.user.first_name + ' respondeu ao seu comentario. Clique para visualizar'
                    notifica.link = reverse("vaga_visualizar", args={pkvaga})
                    notifica.usuario = user
                    notifica.vaga = vaga
                    notifica.save()
                    messages.success(request, mensagens.SUCESSO_ACAO_CONFIRMADA, mensagens.MSG_SUCCESS)
                else:
                    notifica = Notificacao()
                    notifica.tipo = 8
                    notifica.mensagem = request.user.first_name + ' fez um comentário em uma de suas vagas. Clique para visualizar'
                    notifica.link = reverse("vaga_visualizar", args={pkvaga})
                    notifica.usuario = vaga.gerente_vaga.user
                    notifica.vaga = vaga
                    notifica.save()
                    messages.success(request, mensagens.SUCESSO_ACAO_CONFIRMADA, mensagens.MSG_SUCCESS)
            except:
                comentario.user = request.user
                comentario.vaga = vaga
                comentario.text = form.cleaned_data['text']
                comentario.save()

                if request.user.first_name != vaga.gerente_vaga.user.first_name:
                    notifica = Notificacao()
                    notifica.tipo = 8
                    notifica.mensagem = request.user.first_name + 'fez um comentário em uma de suas vagas. Clique para visualizar'
                    notifica.link = reverse("vaga_visualizar", args={pkvaga})
                    notifica.usuario = vaga.gerente_vaga.user
                    notifica.vaga = vaga
                    notifica.save()
                messages.success(request, mensagens.SUCESSO_ACAO_CONFIRMADA, mensagens.MSG_SUCCESS)
    return redirect(visualizar_vaga, pkvaga)

@login_required(login_url='/accounts/login/')
@user_passes_test(is_admin)
def excluir_comentario(request,pkcomentario):
    comment = get_object_or_404(Comentario, pk=pkcomentario)
    vaga= comment.vaga
    comment.delete()
    messages.success(request, mensagens.SUCESSO_ACAO_CONFIRMADA, mensagens.MSG_SUCCESS)
    return redirect(visualizar_vaga, vaga.id)
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
        empresa.user.email = form.cleaned_data['email']
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
        name = form.cleaned_data['name']
        fullname = name.split(' ')
        aluno.user.first_name=fullname[0]
        fullname.remove(fullname[0])
        last_name=""
        for aux in fullname:
            last_name=last_name+" "+aux
        aluno.user.last_name = last_name
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
        name = form.cleaned_data['name']
        fullname = name.split(' ')
        professor.user.first_name = fullname[0]
        fullname.remove(fullname[0])
        last_name = ""
        for aux in fullname:
            last_name = last_name + " " + aux
        professor.user.last_name = last_name
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
            empresa.website = form.cleaned_data['Site'] if form.cleaned_data['Site'] is not None else ""
            empresa.telefone = form.cleaned_data['telefone'] if form.cleaned_data['telefone'] is not None else ""
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

@transaction.atomic
@login_required(login_url='/accounts/login/')
def excluir_empresa(request, pk):
    empresa = get_object_or_404(Empresa, user_id=pk)
    if pk != str(request.user.id):
        messages.error(request, mensagens.ERRO_PERMISSAO_NEGADA, mensagens.MSG_ERRO)
        return HttpResponseRedirect('/home/')
    vagas = Vaga.objects.filter(gerente_vaga=empresa)
    for vaga in vagas:
        if vaga.vencida is False and vaga.situacao == 3:
            messages.error(request, mensagens.ERRO_HA_VAGAS_ATIVAS, mensagens.MSG_ERRO)
            return HttpResponseRedirect(reverse("Exibir_Empresa", args={pk}))
    Vaga.objects.filter(gerente_vaga=empresa, situacao__range=(1,3)).update(situacao=4)
    empresa.user.is_active = False
    empresa.situacao = Empresa.EXCLUIDO
    empresa.save()
    empresa.user.save()
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
@user_passes_test(is_admin)
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
           'Nome_Completo': Nome,
            'Email': aluno.user.email}
    if request.method == 'POST':
        form = FormularioEditarAluno(request.POST, instance=aluno, initial=initial)
        if form.is_valid():
            aluno.curso = form.cleaned_data['curso']
            aluno.telefone = form.cleaned_data['telefone']
            aluno.user.email = form.cleaned_data['Email']
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
            return redirect(exibir_aluno, pk)
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

def upload_curriculo(request,pk):
    aluno = get_object_or_404(Aluno, user_id=pk)
    if pk != str(request.user.id):
        messages.error(request, mensagens.ERRO_PERMISSAO_NEGADA, mensagens.MSG_ERRO)
        return HttpResponseRedirect('/home/')
    if request.method == 'POST':
        form = UploadCurriculo(request.FILES)
        if form.is_valid():
            try:
                try:
                    os.remove(aluno.curriculo.path)
                    aluno.curriculo = request.FILES['curriculo']
                except:
                    aluno.curriculo = request.FILES['curriculo']
                try:
                    validate_file_extension(request.FILES['curriculo'])
                    aluno.curriculo.name = 'Curriculo'+str(pk)+'.pdf'
                    aluno.data_upload_curriculo = timezone.now()
                    aluno.save()
                    messages.success(request, "Upload com sucesso", mensagens.MSG_SUCCESS)
                    return HttpResponseRedirect('/aluno/curriculo/' + str(pk))
                except:
                    messages.error(request, 'Formato não aceito')
            except:
                messages.error(request,'Campo de envio não preenchido')
    else:
        form = UploadCurriculo()
    curriculo = None
    if aluno.curriculo.name != None:
        spl = aluno.curriculo.name.split("/")

        if len(spl) == 2:
            curriculo = spl[1]
    try:
        return render(request, 'sva/aluno/curriculo.html', {'form': form,'curriculo':curriculo,'data':aluno.data_upload_curriculo,'visualizar':aluno.curriculo})
    except:
        return render(request, 'sva/aluno/curriculo.html', {'form': form,'curriculo':curriculo,'data':aluno.data_upload_curriculo,'visualizar':None})
@login_required(login_url='/accounts/login/')
def excluir_curriculo(request, pk):
    aluno = get_object_or_404(Aluno, user_id=pk)
    if pk != str(request.user.id):
        messages.error(request, mensagens.ERRO_PERMISSAO_NEGADA, mensagens.MSG_ERRO)
        return HttpResponseRedirect('/home/')
    if aluno is not None:
        if os.path.isfile(aluno.curriculo.path):
            os.remove(aluno.curriculo.path)
        aluno.curriculo.name = ""
        aluno.save()
        messages.success(request,"Excluido com sucesso", mensagens.MSG_SUCCESS)
        return HttpResponseRedirect('/aluno/curriculo/'+str(pk))

def download_curriculo(request,pk):
    aluno = get_object_or_404(Aluno, user_id=pk)
    if pk != str(request.user.id):
        gerente = GerenteVaga.objects.get(user=request.user)
        if gerente is None:
            messages.error(request, mensagens.ERRO_PERMISSAO_NEGADA, mensagens.MSG_ERRO)
            return HttpResponseRedirect('/home/')
    filename = aluno.curriculo.name.split('/')[-1]
    response = HttpResponse(aluno.curriculo, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename

    return response
###############################################################################
#                                 ACESSO                                      #
###############################################################################


def layout(request):
    form = FormularioContato()
    return render(request, 'sva/layout.html', {'form': form})


def recuperar_senha(request):
    if request.method == "GET":
        return render(request, 'registration/recuperarSenha.html', {})

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
    Email = professor.user.email
    initial = {
        'Nome_Completo': Nome,
        'telefone': Telefone,
        'Curso': Curso,
        'Email': Email}

    if request.method == 'POST':
        form = FormularioEditarProfessor(request.POST, instance=professor, initial=initial)
        if form.is_valid():
            texto = form.cleaned_data['Nome_Completo']
            Nome = texto.split(" ", 1)
            professor.user.email = form.cleaned_data['Email']
            professor.curso = form.cleaned_data['curso']
            professor.siape = form.cleaned_data['siape']
            professor.telefone = form.cleaned_data['telefone']
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

    vagas = Vaga.objects.filter(gerente_vaga=professor)
    do_not_execute = False
    for vaga in vagas:
        if vaga.vencida is False and vaga.situacao == 3:
            do_not_execute = True
    if do_not_execute is False:
        Vaga.objects.filter(gerente_vaga=professor, situacao__range=(1,3)).update(situacao=4)
        professor.user.is_active = False
        professor.situacao = Professor.EXCLUIDO
        professor.user.save()
        professor.save()
        messages.error(request, mensagens.SUCESSO_ACAO_CONFIRMADA, mensagens.MSG_SUCCESS)
        return HttpResponseRedirect('/home/')
    else:
        messages.error(request, mensagens.ERRO_HA_VAGAS_ATIVAS, mensagens.MSG_ERRO)
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


@transaction.atomic
def acessar_notificacao(request):
    pk = request.GET.get('pk', None)
    notificacao = Notificacao.objects.get(pk=pk) if pk or pk!='' else None
    if not notificacao:
        data = {'erro': True}
        return JsonResponse(data)
    notificacao.lida = True
    notificacao.data_leitura = datetime.now()
    notificacao.save()
    data = {
        'sucesso': True,
        'id_link': 'notflink-%d' % notificacao.pk,
        'link': notificacao.link
    }
    return JsonResponse(data)

@csrf_exempt
def gerenciar_areaatuacao(request):
    context={}
    areas=AreaAtuacao.objects.filter(situacao="DEFERIDO");
    areasaaprovar=AreaAtuacao.objects.filter(situacao="AGUARDANDO_APROVACAO");
    context['areas'] = areas
    context['areasaaprovar'] = areasaaprovar

    if request.is_ajax():
        if(request.POST['type']=="edit"):
            area=AreaAtuacao.objects.get(id=int(request.POST['id']))
            contareas = AreaAtuacao.objects.filter(nome=request.POST['data'], situacao="DEFERIDO").count()
            contareas = contareas + AreaAtuacao.objects.filter(nome=request.POST['data'], situacao="INDEFERIDO").count()
            if area.nome == request.POST['data']:
                contareas = contareas-1;
            if contareas:
                messages.success(request, 'Área de atuação já adicionada!', mensagens.MSG_ERRO)
                return redirect(gerenciar_areaatuacao)
            area.nome=request.POST['data']
            # messages.success(request, 'Área de atuação editada com sucesso!', mensagens.MSG_SUCCESS)
            area.save()
            # return redirect(gerenciar_areaatuacao)
        if (request.POST['type']=="delete"):
            AreaAtuacao.objects.get(id=int(request.POST['id'])).delete()
    #        messages.success(request, 'Área de atuação removida com sucesso!', mensagens.MSG_SUCCESS)
            # return redirect(gerenciar_areaatuacao)
        if (request.POST['type'] == "deferida"):
            area = AreaAtuacao.objects.get(id=int(request.POST['id']))
            area.situacao = "DEFERIDO"
          #  messages.success(request, 'Área de atuação aprovada com sucesso!', mensagens.MSG_SUCCESS)
            area.save()
            areas = AreaAtuacao.objects.filter(situacao="DEFERIDO");
            areasaaprovar = AreaAtuacao.objects.filter(situacao="AGUARDANDO_APROVACAO");
            context['areas'] = areas
            context['areasaaprovar'] = areasaaprovar
        return redirect(gerenciar_areaatuacao)

    if request.method == 'POST':
        novaarea = AreaAtuacao()
        if AreaAtuacao.objects.filter(nome=request.POST['new_text']).exists():
            messages.error(request, _('Essa área de atuação já existe'), mensagens.MSG_ERRO)
            return redirect(gerenciar_areaatuacao)
        if request.POST.get('new_text','').isspace() or request.POST.get('new_text','') is '':
            messages.error(request, _('Entrada inválida'), mensagens.MSG_ERRO)
            return redirect(gerenciar_areaatuacao)
        novaarea.nome = request.POST.get('new_text','').strip()
        novaarea.situacao="DEFERIDO"
        novaarea.save()
        messages.success(request, 'Área de atuação criada com sucesso!',mensagens.MSG_SUCCESS)
        return redirect(gerenciar_areaatuacao)

    return render(request, 'sva/vaga/GerenciarAreaAtuacao.html',context)

def render_to_json(request, data):
    return HttpResponse(
        json.dumps(data, ensure_ascii=False),
        mimetype=request.is_ajax() and "application/json" or "text/html"
    )
