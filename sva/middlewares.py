from datetime import timedelta

from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from star_ratings.models import Rating
from django.db.models.signals import m2m_changed
from .models import *


###############################################################################
#                    CONTEXT PROCESSOR  DE NOTIFICAÇÕES                       #
###############################################################################

def notificacoes_context_processor(request):
    context_data = dict()
    context_data['notificacoes'] = Notificacao.objects.filter(usuario=request.user, lida=False)
    return context_data


###############################################################################
#                       SIGNALS  PARA NOTIFICAÇÕES                            #
###############################################################################


class NotificacaoSignals:
    TEXTO_NOTIFICACAO_CADASTRO_PROFESSOR = 'O professor %s se cadastrou no sistema. Clique aqui para moderar o acesso'
    TEXTO_NOTIFICACAO_CADASTRO_EMPRESA = 'A empresa %s deseja acessar o SVA. Clique aqui para liberar ou negar o acesso'
    TEXTO_NOTIFICACAO_INDICACAO_VAGA = '%s indicou a vaga %s pra você. Clique para visualizar'
    TEXTO_NOTIFICACAO_CADASTRO_VAGA = '%s cadastrou uma nova vaga. Clique para visualizar'
    TEXTO_NOTIFICACAO_APROVACAO_VAGA = 'Sua vaga %s foi APROVADA Clique para visualizar'
    TEXTO_NOTIFICACAO_REPROVACAO_VAGA = 'Sua vaga %s foi REPROVADA Clique para visualizar'
    TEXTO_NOTIFICACAO_NOVOS_CANDIDATOS_VAGA = '%d novas pessoas se cadastraram na sua vaga %s'
    TEXTO_NOTIFICACAO_SOLICITACAO_AREA = '%s solicitou uma nova área de atuação. Clique para verificar.'
    TEXTO_NOTIFICACAO_NOVA_MENSAGEM_FORUM = '%s cadastrou uma nova pergunta no fórum da vaga %. Clique para visualizar'
    TEXTO_NOTIFICACAO_RESPOSTA_FORUM = '%s respondeu sua pergunta na vaga %. Clique para visualizar'

    @receiver(post_save, sender=Vaga)
    def cria_notificacao_cadastro_vaga(sender, instance, created, **kwargs):
        if created:
            grupos_admin = Group.objects.filter(name__in=['Administrador', 'Setor de Estágios'])
            usuarios = User.objects.filter(groups__in=grupos_admin)
            for usuario in usuarios:
                notificacao = Notificacao()
                notificacao.tipo = Notificacao.TIPO_CADASTRO_VAGA
                notificacao.vaga = instance
                notificacao.usuario = usuario
                notificacao.mensagem = NotificacaoSignals.TEXTO_NOTIFICACAO_CADASTRO_VAGA % instance.gerente_vaga.user.first_name
                notificacao.link = reverse("vaga_visualizar", args={instance.pk})
                notificacao.save()

    @receiver(post_save, sender=Empresa)
    def cria_notificacao_cadastro_empresa(sender, instance, created, **kwargs):
        if created:
            grupos = Group.objects.filter(name__in=['Administrador', 'Setor de Estágios'])
            usuarios = User.objects.filter(Q(groups__in=grupos) | Q(is_superuser=True))
            for usuario in usuarios:
                notificacao = Notificacao()
                notificacao.tipo = Notificacao.TIPO_CADASTRO_EMPRESA
                notificacao.vaga = None
                notificacao.usuario = usuario
                notificacao.mensagem = NotificacaoSignals.TEXTO_NOTIFICACAO_CADASTRO_EMPRESA % instance.nome
                notificacao.link = reverse("Exibir_Empresa", args={instance.user.pk})
                notificacao.save()

    @receiver(post_save, sender=Professor)
    def cria_notificacao_cadastro_professor(sender, instance, created, **kwargs):
        if created:
            grupos = Group.objects.filter(name__in=['Administrador', 'Setor de Estágios'])
            usuarios = User.objects.filter(Q(groups__in=grupos) | Q(is_superuser=True))
            for usuario in usuarios:
                notificacao = Notificacao()
                notificacao.tipo = Notificacao.TIPO_CADASTRO_PROFESSOR
                notificacao.vaga = None
                notificacao.usuario = usuario
                notificacao.mensagem = NotificacaoSignals.TEXTO_NOTIFICACAO_CADASTRO_PROFESSOR % instance.user.first_name
                notificacao.link = reverse("Exibir_Professor", args={instance.user.pk})
                notificacao.save()

    @receiver(post_save, sender=Vaga)
    def cria_notificacao_aprovacao_vaga(sender, instance, created, **kwargs):
        # Verifica se a aprovação é recente (realizada no último minuto):
        um_minuto_atras = datetime.now() - timedelta(seconds=-60)
        if not created and instance.data_aprovacao and instance.data_aprovacao > um_minuto_atras:
            # Gera uma notificação pro Gerente
            gerente = instance.gerente_vaga
            notificacao = Notificacao()
            notificacao.tipo = Notificacao.TIPO_CADASTRO_VAGA
            notificacao.vaga = instance
            notificacao.usuario = gerente.user
            notificacao.mensagem = NotificacaoSignals.TEXTO_NOTIFICACAO_APROVACAO_VAGA % Vaga.titulo
            notificacao.link = reverse("vaga_visualizar", args={instance.pk})
            notificacao.save()
            # Gera uma notificação pros alunos interessados (se a vaga for compatível com a área de atuação ou curso)
            alunos = Aluno.objects.filter(Q(areas_atuacao__in=instance.areas_atuacao) | Q(curso__in=instance.cursos)).distinct()
            for aluno in alunos:
                notificacao = Notificacao()
                notificacao.tipo = Notificacao.TIPO_CADASTRO_VAGA
                notificacao.vaga = instance
                notificacao.usuario = aluno.user
                notificacao.mensagem = NotificacaoMiddleware.TEXTO_NOTIFICACAO_CADASTRO_VAGA % instance.gerente_vaga.nome
                notificacao.link = reverse("vaga_visualizar", args={instance.pk})
                notificacao.save()

    @receiver(post_save, sender=Vaga)
    def cria_notificacao_reprovacao_vaga(sender, instance, created, **kwargs):
        if not created and instance.situacao == Vaga.REPROVADA:
            gerente = instance.gerente_vaga
            notificacao = Notificacao()
            notificacao.tipo = Notificacao.TIPO_REPROVACAO_VAGA
            notificacao.vaga = instance
            notificacao.usuario = gerente.user
            notificacao.mensagem = NotificacaoSignals.TEXTO_NOTIFICACAO_REPROVACAO_VAGA % Vaga.titulo
            notificacao.link = reverse("vaga_editar", args={instance.pk})
            notificacao.save()

    @receiver(m2m_changed, sender=Vaga.alunos_inscritos.through)
    def cria_notificacao_candidatura_aluno(sender, instance, **kwargs):
        pk_set = kwargs.pop('pk_set', None)
        action = kwargs.pop('action', None)
        if action == "pre_add":  # Quando um aluno se candidata a uma vaga
            notificacao_anterior = Notificacao.objects.filter(vaga=instance, lida=False, tipo=Notificacao.TIPO_NOVOS_CANDIDATOS).first()
            if notificacao_anterior:  # Se já há uma notificação, só altera o número de novos candidatos
                qtde_candidatos = int(notificacao_anterior.mensagem.split(' ')[0]) + len(pk_set)
                notificacao_anterior.mensagem = NotificacaoSignals.TEXTO_NOTIFICACAO_NOVOS_CANDIDATOS_VAGA % (qtde_candidatos, instance.titulo)
                notificacao_anterior.save()
            else:  # Caso não haja notificação para esse evento ainda, é criada uma nova
                qtde_candidatos = len(pk_set)
                notificacao = Notificacao()
                notificacao.tipo = Notificacao.TIPO_NOVOS_CANDIDATOS
                notificacao.vaga = instance
                notificacao.usuario = instance.gerente_vaga.user
                notificacao.mensagem = NotificacaoSignals.TEXTO_NOTIFICACAO_NOVOS_CANDIDATOS_VAGA % (qtde_candidatos, instance.titulo)
                notificacao.link = reverse("vaga_visualizar", args={instance.pk})
                notificacao.save()


###############################################################################
#                          SIGNALS PARA AVALIAÇÕES                            #
###############################################################################


@receiver(post_save, sender=Rating)
def avaliacao_counter(sender, instance, created, **kwargs):
    if instance.content_type_id == ContentType.objects.get(app_label='sva', model='vaga').pk:
        vaga = Vaga.objects.get(pk=instance.object_id)
        vaga.nota_media = instance.average
        vaga.save()
    elif instance.content_type_id == ContentType.objects.get(app_label='sva', model='professor').pk:
        professor = Professor.objects.get(pk=instance.object_id)
        professor.nota_media = instance.average
        professor.save()
    elif instance.content_type_id == ContentType.objects.get(app_label='sva', model='empresa').pk:
        empresa = Empresa.objects.get(pk=instance.object_id)
        empresa.nota_media = instance.average
        empresa.save()
