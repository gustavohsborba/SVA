# -*- coding: utf-8 -*- 

from django.utils.translation import gettext_lazy as _

from django.contrib.auth.models import *
from django.core.validators import *
from .validators import *
from django.db import models

# Create your models here.

class Campus(models.Model):
    class Meta:
        verbose_name_plural = _('campi')

    CIDADE_CHOICES = {
        ('BELO HORIZONTE', 'Belo Horizonte'),
        ('LEOPOLDINA', 'Leopoldina'),
        ('ARAXA', 'Araxá'),
        ('DIVINOPOLIS', 'Divinópolis'),
        ('VARGINHA', 'Varginha'),
        ('TIMOTEO', 'Timóteo'),
        ('NEPOMUCENO', 'Nepomuceno'),
        ('CURVELO', 'Curvelo'),
        ('CONTAGEM', 'Contagem')
    }

    nome = models.CharField(max_length=45, null=False)
    cidade = models.CharField(max_length=45, null=False, choices=CIDADE_CHOICES)
    sigla = models.CharField(max_length=5, null=False, unique=True, validators=[validate_sigla])

    def __str__(self):
        return '%s (%s)' % (self.nome, self.cidade)


class Curso(models.Model):
    NIVEL_ENSINO_CHOICES = {
        (1, 'TECNICO'),
        (2, 'GRADUACAO'),
        (3, 'MESTRADO'),
        (4, 'DOUTORADO'),
        (5, 'ESPECIALIZACAO')
    }
    campus = models.ManyToManyField(to=Campus, related_name='campi')

    nome = models.CharField(max_length=45, null=False, unique=True)
    sigla = models.CharField(max_length=5, null=False, unique=True, validators=[validate_sigla])
    nivel_ensino = models.IntegerField(verbose_name='Nível de Ensino', null=False, choices=NIVEL_ENSINO_CHOICES)

    def __str__(self):
        return '%s (%s)' % (self.nome, self.nivel_ensino)


class Habilidade(models.Model):
    nome = models.CharField(max_length=45, null=False, unique=True, db_index=True)

    def __str__(self):
        return '%s' % self.nome


class AreaAtuacao(models.Model):
    class Meta:
        verbose_name = 'Área de Atuação'
        verbose_name_plural = 'Áreas de Atuação'
    nome = models.CharField(max_length=45, null=False, unique=True, db_index=True)

    def __str__(self):
        return '%s' % self.nome


class Aluno(User):
    class Meta:
        verbose_name = 'Aluno'
        verbose_name_plural = 'Alunos'

    user = models.ForeignKey(to=User, on_delete=models.CASCADE, null=False, related_name='alunos')
    curso = models.ForeignKey(to=Curso, null=False, blank=False)
    habilidades = models.ManyToManyField(to=Habilidade, related_name='alunos')
    areas_atuacao = models.ManyToManyField(to=AreaAtuacao, related_name='alunos')

    cpf = models.CharField(unique=True, max_length=14, validators=[validate_CPF])
    telefone = models.CharField(max_length=20, null=True, validators=[validate_integer])
    data_cadastro = models.DateTimeField(verbose_name='Data de Cadastro', auto_now_add=True, blank=False)
    data_fim = models.DateTimeField(verbose_name='Data de Cancelamento', blank=True, null=True)

    def __str__(self):
        return '%s %s (%s)' % (self.user.first_name, self.user.last_name, self.cpf)


class GerenteVaga(User):
    class Meta:
        verbose_name = 'Gerente de Vagas'
        verbose_name_plural = 'Gerentes de Vagas'

    user = models.ForeignKey(to=User, on_delete=models.CASCADE, null=False, related_name='gerentes_vaga')

    nome = models.CharField(max_length=60, null=False, blank=False, db_index=True)
    nota_media = models.FloatField(null=False, default=0.0)
    data_cadastro = models.DateTimeField(verbose_name='Data de Cadastro', auto_now_add=True, blank=False)
    data_fim = models.DateTimeField(verbose_name='Data de Cancelamento', blank=True, null=True)

    def __str__(self):
        return '%s %s' % (self.user.first_name, self.user.last_name)


class Empresa(GerenteVaga):
    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'

    cnpj = models.CharField(unique=True, max_length=14, validators=[validate_CNPJ])

    def __str__(self):
        return '%s %s (%s)' % (self.user.first_name, self.user.last_name, self.cnpj)


class Professor(GerenteVaga):
    class Meta:
        verbose_name = 'Professor'
        verbose_name_plural = 'Professores'

    curso = models.ForeignKey(to=Curso, null=True)

    siape = models.CharField(unique=True, max_length=8, validators=[integer_validator])
    cpf = models.CharField(unique=True, max_length=14, validators=[validate_CPF])

    def __str__(self):
        return '%s %s (%s)' % (self.user.first_name, self.user.last_name, self.curso)


class Vaga(models.Model):
    class Meta:
        get_latest_by = 'data_submissao'
        ordering = ['-data_submissao', '-valor_bolsa']
        permissions = (('can_evaluate_vaga', 'Pode avaliar vaga'),
                       ('can_recommend_vaga', 'Pode indicar vaga'),
                       ('can_approve_vaga', 'Pode aprovar vaga'),
                       ('can_moderate_vaga', 'Pode moderar o fórum da vaga'),)

    gerente_vaga = models.ForeignKey(to=GerenteVaga, null=False, blank=False, related_name='vagas')
    area_atuacao = models.ManyToManyField(to=AreaAtuacao, related_name='vagas')

    titulo = models.CharField(verbose_name='Título', max_length=255, null=False, blank=False, db_index=True)
    descricao = models.TextField(verbose_name='Descrição', null=False, blank=False)
    data_submissao = models.DateTimeField(verbose_name='Data de Submissão', auto_now_add=True, blank=False)
    data_validade = models.DateTimeField(verbose_name='Data de Validade', blank=True, null=True)
    carga_horaria_semanal = models.PositiveIntegerField(verbose_name='Carga Horária Semanal', null=False, blank=False, validators=[integer_validator])
    local = models.CharField(verbose_name='Local de Trabalho', max_length=255, null=False, blank=False)
    valor_bolsa = models.FloatField(verbose_name='Valor da Bolsa', null=False, blank=False, )
    beneficios = models.TextField(verbose_name='Benefícios', null=True, blank=True)
    nota_media = models.FloatField(verbose_name='Nota', null=False, blank=False, default=0.0)
    data_aprovacao = models.DateTimeField(verbose_name='Data de Aprovação', blank=True, null=True)
    usuario_aprovacao = models.CharField(verbose_name='Responsável pela aprovação', max_length=60, blank=True, null=True)

    def __str__(self):
        return '%s - %s' % (self.titulo, self.gerente_vaga.nome)


class Notificacao(models.Model):
    class Meta:
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'
        get_latest_by = 'data_cadastro'
        ordering = ['-data_cadastro']

    TIPO_INDICACAO = 1
    TIPO_CADASTRO_PROFESSOR = 2
    TIPO_CADASTRO_EMPRESA = 3
    TIPO_CADASTRO_VAGA = 4
    TIPO_APROVACAO_VAGA = 5
    TIPO_VAGA_INTERESSE = 6
    TIPO_SOLICITACAO_AREA_ATUACAO = 7
    TIPO_NOVA_MENSAGEM_FORUM = 8
    TIPO_RESPOSTA_FORUM = 9

    TIPO_NOTIFICACAO_CHOICES = {(TIPO_INDICACAO, 'Indicação de Vaga'),
                                (TIPO_CADASTRO_PROFESSOR, 'Cadastro de Professor'),
                                (TIPO_CADASTRO_EMPRESA, 'Cadastro de Empresa'),
                                (TIPO_CADASTRO_VAGA, 'Cadastro de Vaga'),
                                (TIPO_APROVACAO_VAGA, 'Aprovação de Vaga'),
                                (TIPO_VAGA_INTERESSE, 'Vaga de Interesse'),
                                (TIPO_SOLICITACAO_AREA_ATUACAO, 'Solicitação de Área de Atuação'),
                                (TIPO_NOVA_MENSAGEM_FORUM, 'Nova Mensagem no Fórum'),
                                (TIPO_RESPOSTA_FORUM, 'Resposta no Fórum')}

    vaga = models.ForeignKey(to=Vaga, null=True, blank=True, on_delete=models.CASCADE, related_name='notificacoes')
    usuario = models.ForeignKey(to=User, null=True, blank=True, on_delete=models.CASCADE, related_name='notificacoes')

    tipo = models.PositiveIntegerField(verbose_name='Tipo da Notificação', null=False, choices=TIPO_NOTIFICACAO_CHOICES)
    data_cadastro = models.DateTimeField(verbose_name='Data de Cadastro', auto_now_add=True, blank=False)
    mensagem = models.TextField(null=False, blank=False)

    def __str__(self):
        return '%s' % self.mensagem


class FiltroPesquisa(models.Model):
    class Meta:
        verbose_name = 'Filtro de Pesquisa'
        verbose_name_plural = 'Filtros de Pesquisa'

    aluno = models.ForeignKey(to=Aluno, null=True, blank=True, on_delete=models.CASCADE, related_name='filtros_pesquisa')

    nome = models.CharField(verbose_name='Nome do Filtro', max_length=255, null=False, blank=False)
    chave = models.CharField(max_length=255, null=False, blank=False)
    valor = models.CharField(max_length=255, null=False, blank=False)

    def __str__(self):
        return '%s - %s' % (self.nome, self.chave)

