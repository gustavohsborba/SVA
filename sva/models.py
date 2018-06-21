# -*- coding: utf-8 -*-
from datetime import datetime

from django.utils.translation import gettext_lazy as _

from django.contrib.auth.models import *
from django.core.validators import *
from .validators import *
from django.db import models

# Create your models here.


class Campus(models.Model):
    class Meta:
        verbose_name = _('campus')
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

    nome = models.CharField(max_length=45, null=False, blank=False)
    cidade = models.CharField(max_length=45, null=False, blank=False, choices=CIDADE_CHOICES)
    sigla = models.CharField(max_length=5, null=False, blank=False, unique=True, validators=[validate_sigla])

    def __str__(self):
        return '%s (%s)' % (self.nome, self.cidade)


class Curso(models.Model):
    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'

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
        return '%s (%s)' % (self.nome, self.get_nivel_ensino_display())


class Habilidade(models.Model):
    nome = models.CharField(max_length=45, null=False, unique=True, db_index=True)

    def __str__(self):
        return '%s' % self.nome


class AreaAtuacao(models.Model):
    DEFERIDO = 'DEFERIDO'
    AGUARDANDO_APROVACAO = 'AGUARDANDO_APROVACAO'

    SITUACAO_AREA_ATUACAO_CHOICES = {
                (DEFERIDO, 'Deferido'),
                (AGUARDANDO_APROVACAO, 'Aguardando Aprovação'),
    }

    class Meta:
        verbose_name = 'Área de Atuação'
        verbose_name_plural = 'Áreas de Atuação'
        permissions = (('can_request_area_atuacao', 'Pode solicitar área de atuação'),
                       ('can_release_area_atuacao', 'Pode liberar área de atuaçãos'))

    area_mae = models.ForeignKey('self', blank=True, null=True)
    nome = models.CharField(max_length=45, null=False, unique=True, db_index=True)
    situacao = models.CharField(verbose_name='Situação', max_length=30, choices=SITUACAO_AREA_ATUACAO_CHOICES,
                                blank=False, null=False, default='AGUARDANDO_APROVACAO')

    def __str__(self):
        return '%s' % self.nome


class Aluno(models.Model):
    class Meta:
        verbose_name = 'Aluno'
        verbose_name_plural = 'Alunos'

    user = models.ForeignKey(to=User, on_delete=models.PROTECT, null=False, related_name='alunos')
    curso = models.ForeignKey(to=Curso, null=False, blank=False, on_delete=models.PROTECT)
    habilidades = models.ManyToManyField(to=Habilidade, related_name='alunos', blank=True)
    areas_atuacao = models.ManyToManyField(to=AreaAtuacao, related_name='alunos', blank=True)
    endereco = models.CharField(max_length=255, null=True)
    matricula = models.CharField(max_length=12, null=True, validators=[validate_integer])
    cpf = models.CharField(unique=True, max_length=14, validators=[validate_CPF])
    telefone = models.CharField(max_length=20, null=True, validators=[validate_integer])
    data_cadastro = models.DateTimeField(verbose_name='Data de Cadastro', auto_now_add=True, blank=False)
    data_fim = models.DateTimeField(verbose_name='Data de Cancelamento', blank=True, null=True)
    curriculo = models.FileField(upload_to="curriculo/", blank=True, null=True)
    data_upload_curriculo = models.DateTimeField(verbose_name='Data de upload', null=True)

    def save(self, *args, **kwargs):
        self.user.username = self.cpf
        self.user.groups.add(Group.objects.get(name='Aluno'))
        self.user.save()
        super(Aluno, self).save(*args, **kwargs)

    @property
    def ativo(self):
        return self.user.is_active

    def __str__(self):
        return '%s %s (%s - %s)' % (self.user.first_name, self.user.last_name, self.matricula, self.curso.sigla)


class GerenteVaga(models.Model):
    class Meta:
        verbose_name = 'Gerente de Vagas'
        verbose_name_plural = 'Gerentes de Vagas'
        permissions = (('can_request_gerente_vaga', 'Pode solicitar criação de gerente'),
                       ('can_release_gerente_vaga', 'Pode liberar criação de gerente'))

    DEFERIDO = 'DEFERIDO'
    INDEFERIDO = 'INDEFERIDO'
    AGUARDANDO_APROVACAO = 'AGUARDANDO_APROVACAO'
    EXCLUIDO = 'EXCLUIDO'

    SITUACAO_GERENTE_VAGA_CHOICES = {
        (DEFERIDO, 'Deferido'),
        (INDEFERIDO, 'Indeferido'),
        (AGUARDANDO_APROVACAO, 'Aguardando Aprovação'),
        (EXCLUIDO, 'Excluído'),
    }

    user = models.ForeignKey(to=User, on_delete=models.PROTECT, null=False, related_name='gerentes_vaga')
    nota_media = models.FloatField(null=False, default=0.0)
    data_aprovacao = models.DateTimeField(verbose_name='Data de Aprovação', null=True, blank=True)
    data_fim = models.DateTimeField(verbose_name='Data de Cancelamento', blank=True, null=True)
    situacao = models.CharField(verbose_name='Situação', max_length=30, choices=SITUACAO_GERENTE_VAGA_CHOICES, blank=False, null=False, default='AGUARDANDO_APROVACAO')

    @property
    def ativo(self):
        return self.user.is_active

    def __str__(self):
        return '%s %s' % (self.user.first_name, self.user.last_name)


class Empresa(GerenteVaga):
    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'

    cnpj = models.CharField(unique=True, max_length=14, validators=[validate_CNPJ])
    nome = models.CharField(max_length=60, null=False, blank=False, db_index=True)
    website = models.CharField(max_length=255, null=True, blank=True, validators=[URLValidator])
    endereco = models.CharField(max_length=255, null=True, blank=True)
    telefone = models.CharField(max_length=20, null=True, blank=True, validators=[validate_integer])

    def save(self, *args, **kwargs):
        self.user.first_name = self.nome
        self.user.username = self.cnpj
        self.user.groups.add(Group.objects.get(name='Gerente Vagas'))
        self.user.groups.add(Group.objects.get(name='Empresa'))
        self.user.save()
        if not self.pk:
            # se ainda não está no banco -> Está sendo Criado
            self.user.is_active = False
            self.user.is_staff = False
        super(Empresa, self).save(*args, **kwargs)

    def __str__(self):
        return '%s (%s)' % (self.nome, self.cnpj)


class Professor(GerenteVaga):
    class Meta:
        verbose_name = 'Professor'
        verbose_name_plural = 'Professores'

    curso = models.ForeignKey(to=Curso, null=True, blank=False, on_delete=models.PROTECT)
    telefone = models.CharField(max_length=20, null=True, validators=[validate_integer])

    siape = models.CharField(unique=True, max_length=8, blank=False, null=False, validators=[integer_validator])
    cpf = models.CharField(unique=True, max_length=14, blank=False, null=False,  validators=[validate_CPF])

    def save(self, *args, **kwargs):
        self.user.username = self.cpf
        self.user.groups.add(Group.objects.get(name='Gerente Vagas'))
        self.user.groups.add(Group.objects.get(name='Professor'))
        self.user.save()
        if not self.pk:
            # se ainda não está no banco -> Está sendo Criado
            self.user.is_active = False
            self.user.is_staff = False
        super(Professor, self).save(*args, **kwargs)

    def __str__(self):
        return '%s %s' % (self.user.first_name, self.user.last_name)


class Vaga(models.Model):

    class Meta:
        get_latest_by = 'data_submissao'
        ordering = ['-data_submissao', '-valor_bolsa']
        permissions = (('can_evaluate_vaga', 'Pode avaliar vaga'),
                       ('can_recommend_vaga', 'Pode indicar vaga'),
                       ('can_approve_vaga', 'Pode aprovar vaga'),
                       ('can_moderate_vaga', 'Pode moderar o fórum da vaga'),)

    CADASTRADA = 1
    EDITADA = 2
    ATIVA = 3
    INATIVA = 4
    REPROVADA = 5

    SITUACAO_VAGA_CHOICES = {
        (CADASTRADA, 'Cadastrada'),
        (EDITADA, 'Editada'),
        (ATIVA, 'Ativa'),
        (INATIVA, 'Inativa'),
        (REPROVADA, 'Reprovada')
    }

    TIPO_VAGA_CHOICES = {
        (1, 'Estágio'),
        (2, 'Monitoria'),
        (3, 'Iniciação Científica'),
        (4, 'Outro')
    }

    gerente_vaga = models.ForeignKey(to=GerenteVaga, null=False, blank=False, related_name='vagas')
    usuario_aprovacao = models.ForeignKey(to=User, null=True, blank=True, related_name='vagas_aprovadas')
    areas_atuacao = models.ManyToManyField(to=AreaAtuacao, related_name='vagas')
    cursos = models.ManyToManyField(to=Curso, blank=True, related_name='vagas_atribuidas')
    alunos_inscritos = models.ManyToManyField(to=Aluno, blank=True, related_name='vagas_inscritas')
    alunos_interessados = models.ManyToManyField(to=Aluno, blank=True, related_name='vagas_interesse')
    avaliacoes = models.ManyToManyField(Aluno, through='Avaliacao', blank=True, related_name='avaliacao_vaga')

    titulo = models.CharField(verbose_name='Título', max_length=255, null=False, blank=False, db_index=True)
    descricao = models.TextField(verbose_name='Descrição', null=False, blank=False)
    data_submissao = models.DateTimeField(verbose_name='Data de Submissão', auto_now_add=True, blank=False)
    data_alteracao = models.DateTimeField(verbose_name='Data da última alteração', auto_now=True, blank=False)
    data_validade = models.DateTimeField(verbose_name='Data de Validade', blank=True, null=True)
    carga_horaria_semanal = models.PositiveIntegerField(verbose_name='Carga Horária Semanal', null=False, blank=False, validators=[integer_validator])
    local = models.CharField(verbose_name='Local de Trabalho', max_length=255, null=False, blank=False)
    valor_bolsa = models.FloatField(verbose_name='Valor da Bolsa', null=False, blank=False)
    beneficios = models.TextField(verbose_name='Benefícios', null=True, blank=True)
    nota_media = models.FloatField(verbose_name='Nota', null=False, blank=False, default=0.0)
    data_aprovacao = models.DateTimeField(verbose_name='Data de Aprovação', blank=True, null=True)
    situacao = models.IntegerField(verbose_name='Situação', null=False, blank=False, default=1, choices=SITUACAO_VAGA_CHOICES)
    tipo_vaga = models.IntegerField(verbose_name='Tipo da Vaga', null=False, blank=False, default=4, choices=TIPO_VAGA_CHOICES)

    @property
    def vencida(self):
        if self.data_validade is None:
            return False
        return datetime.now() > self.data_validade

    def __str__(self):
        return '%s - %s' % (self.titulo, self.gerente_vaga.user.first_name)

models.signals.post_init.connect(verificaValidade, Vaga)

class Avaliacao(models.Model):
    aluno_avaliador = models.ForeignKey(Aluno, blank=False, null=False)
    vaga_avaliada = models.ForeignKey(Vaga, blank=False, null=False)

    nota = models.IntegerField(verbose_name='Nota atribuída', null=False, blank=False)


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
    TIPO_REPROVACAO_VAGA = 10
    TIPO_NOVOS_CANDIDATOS = 11

    TIPO_NOTIFICACAO_CHOICES = {(TIPO_INDICACAO, 'Indicação de Vaga'),
                                (TIPO_CADASTRO_PROFESSOR, 'Cadastro de Professor'),
                                (TIPO_CADASTRO_EMPRESA, 'Cadastro de Empresa'),
                                (TIPO_CADASTRO_VAGA, 'Cadastro de Vaga'),
                                (TIPO_APROVACAO_VAGA, 'Aprovação de Vaga'),
                                (TIPO_VAGA_INTERESSE, 'Vaga de Interesse'),
                                (TIPO_SOLICITACAO_AREA_ATUACAO, 'Solicitação de Área de Atuação'),
                                (TIPO_NOVA_MENSAGEM_FORUM, 'Nova Mensagem no Fórum'),
                                (TIPO_REPROVACAO_VAGA, 'Vaga Reprovada'),
                                (TIPO_NOVOS_CANDIDATOS, 'Novos Candidatos'),
                                (TIPO_RESPOSTA_FORUM, 'Resposta no Fórum')}

    vaga = models.ForeignKey(to=Vaga, null=True, blank=True, on_delete=models.CASCADE, related_name='notificacoes')
    usuario = models.ForeignKey(to=User, null=True, blank=True, on_delete=models.CASCADE, related_name='notificacoes')

    tipo = models.PositiveIntegerField(verbose_name='Tipo da Notificação', null=False, choices=TIPO_NOTIFICACAO_CHOICES)
    data_cadastro = models.DateTimeField(verbose_name='Data de Cadastro', auto_now_add=True, blank=False)
    mensagem = models.TextField(null=False, blank=False)
    lida = models.BooleanField(null=False, blank=False, default=False)
    data_leitura = models.DateTimeField(verbose_name='Data de visualização', null=True, blank=True)
    link = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return 'Para: %s %s\nMensagem: %s' % (self.usuario.first_name, self.usuario.last_name, self.mensagem)

class Filtro(models.Model):
    class Meta:
        verbose_name = 'Filtro'
        verbose_name_plural = 'Filtros'

    TODOS = 1
    VAGA = 2
    GERENTE = 3
    AREAS = 4
    CURSOS = 5
    DESCRICAO = 6
    LOCAL = 7

    TIPO_CHOICES = {
        (TODOS, 'Todos os campos'),
        (VAGA, 'Nome de vagas'),
        (GERENTE, 'Gerentes e/ou professores'),
        (AREAS, 'Áreas de atuação'),
        (CURSOS, 'Cursos'),
        (DESCRICAO, 'Descrição'),
        (LOCAL, 'Local')
    }

    tipo = models.PositiveIntegerField(verbose_name='Tipo do filtro', null=False, blank=False, default=TODOS, choices=TIPO_CHOICES)
    texto = models.TextField(max_length=255, null=True, blank=True)
    areas_atuacao = models.ForeignKey(to=AreaAtuacao, on_delete=models.CASCADE, blank=True, null=True, related_name='filtro')
    cursos = models.ForeignKey(to=Curso, on_delete=models.CASCADE, blank=True, null=True, related_name='filtro')

class FiltroPesquisa(models.Model):
    class Meta:
        verbose_name = 'Filtro de Pesquisa'
        verbose_name_plural = 'Filtros de Pesquisa'

    MAIS_RECENTES = 1
    MAIS_INSCRITAS = 2
    MELHORES_AVALIACOES = 3
    MAIS_COMENTADAS = 4
    MENOR_PRAZO_INSCRICAO = 5

    ORDENACAO_CHOICES = {
        (MAIS_RECENTES, 'Mais recentes'),
        (MAIS_INSCRITAS, 'Mais inscritas'),
        (MELHORES_AVALIACOES, 'Melhores avaliações'),
        (MAIS_COMENTADAS, 'Mais comentadas'),
        (MENOR_PRAZO_INSCRICAO, 'Menor prazo de inscrição')
    }

    ATIVAS = 1
    PENDENTES = 2
    INATIVAS = 3
    REPROVADAS = 4
    TODAS = 5

    SITUACAO_CHOICES = {
        (ATIVAS, 'Ativas'),
        (PENDENTES, 'Pendentes de avaliação'),
        (INATIVAS, 'Inativas'),
        (REPROVADAS, 'Reprovadas'),
        (TODAS, 'Todas')
    }

    NENHUM_SELECIONADO = 0
    TECNICO = 1
    GRADUACAO = 2
    MESTRADO = 3
    DOUTORADO = 4
    ESPECIALIZACAO = 5

    NIVEL_CHOICES = {
        (NENHUM_SELECIONADO, 'Qualquer'),
        (TECNICO, 'Técnico'),
        (GRADUACAO, 'Graduação'),
        (MESTRADO, 'Mestrado'),
        (DOUTORADO, 'Doutorado'),
        (ESPECIALIZACAO, 'Especialização')
    }

    AVALIACAO_CHOICES = {
        (0, 'Nenhuma avaliação'),
        (1, 'Uma estrela'),
        (2, 'Duas estrelas'),
        (3, 'Três estrelas'),
        (4, 'Quatro estrelas'),
        (5, 'Cinco estrelas')
    }

    user = models.ForeignKey(to=User, null=True, blank=True, on_delete=models.CASCADE, related_name='filtro_pesquisa')
    filtros = models.ManyToManyField(to=Filtro, related_name='pesquisa')

    nome = models.CharField(verbose_name='Nome do Filtro', max_length=255, null=False, blank=False)
    ordenacao = models.PositiveIntegerField(verbose_name='Forma de ordenação dos resultados', null=False, default=MAIS_RECENTES, choices=ORDENACAO_CHOICES)
    situacao = models.PositiveIntegerField(verbose_name='Situação das vagas', null=False, default=ATIVAS, choices=SITUACAO_CHOICES)
    tipo_estagio = models.BooleanField(default=True)
    tipo_ic = models.BooleanField(default=True)
    tipo_monitoria = models.BooleanField(default=True)
    tipo_outros = models.BooleanField(default=True)
    nivel = models.PositiveIntegerField(verbose_name='Situação das vagas', null=True, choices=NIVEL_CHOICES)
    carga_horaria_minima = models.PositiveIntegerField(verbose_name='Carga horária semanal mínima', default=5, null=False,
                                                        validators=[integer_validator])
    carga_horaria_maxima = models.PositiveIntegerField(verbose_name='Carga horária semanal máxima', default=45, null=False,
                                                       validators=[integer_validator])
    salario = models.FloatField(verbose_name='Valor salarial', null=True, blank=True)
    avaliacao = models.IntegerField(verbose_name='Avaliação das vagas', default=0, null=False, choices=AVALIACAO_CHOICES)

    def __str__(self):
        return '%s' % (self.nome)


class Comentario(models.Model):
    vaga = models.ForeignKey(to=Vaga,null=True, blank=True, on_delete=models.CASCADE,related_name='comentario')
    user = models.ForeignKey(to=User, null=True, blank=True, on_delete=models.CASCADE,related_name='comentario')
    text = models.TextField(max_length=300,null=False, blank=False)
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.text

