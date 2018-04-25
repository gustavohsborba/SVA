from datetime import datetime, timedelta

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *

class NotificacaoMiddleware:

    TEXTO_NOTIFICACAO_INDICACAO_VAGA = '%s cadastrou uma nova vaga. Clique para visualizar'
    TEXTO_NOTIFICACAO_CADASTRO_PROFESSOR = '%s cadastrou uma nova vaga. Clique para visualizar'
    TEXTO_NOTIFICACAO_CADASTRO_EMPRESA = '%s cadastrou uma nova vaga. Clique para visualizar'
    TEXTO_NOTIFICACAO_CADASTRO_VAGA = '%s cadastrou uma nova vaga. Clique para visualizar'
    TEXTO_NOTIFICACAO_APROVACAO_VAGA = '%s cadastrou uma nova vaga. Clique para visualizar'
    TEXTO_NOTIFICACAO_SOLICITACAO_AREA = '%s cadastrou uma nova vaga. Clique para visualizar'
    TEXTO_NOTIFICACAO_NOVA_MENSAGEM_FORUM = '%s cadastrou uma nova vaga. Clique para visualizar'
    TEXTO_NOTIFICACAO_RESPOSTA_FORUM = '%s cadastrou uma nova vaga. Clique para visualizar'

    @receiver(post_save, sender=Vaga)
    def cria_notificacao_cadastro_vaga(sender, instance, created, **kwargs):
        if created:
            grupos_admin = Group.objects.filter(name__in=['Administrador', 'Setor de Estágios'])
            usuarios = User.objects.filter(groups__in=grupos_admin)
            for usuario in usuarios:
                notificacao = Notificacao()
                notificacao.tipo = 4  # Cadastro de Vaga
                notificacao.vaga = instance
                notificacao.usuario = usuario
                notificacao.mensagem = NotificacaoMiddleware.TEXTO_NOTIFICACAO_CADASTRO_VAGA % instance.gerente_vaga.nome
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
            notificacao.mensagem = NotificacaoMiddleware.TEXTO_NOTIFICACAO_CADASTRO_VAGA % instance.gerente_vaga.nome
            notificacao.save()

            # Gera uma notificação pros alunos interessados:
            # (Ainda não sabemos se as vagas vão ser implementadas por habilidades ou por Áreas de Atuação)
            #habilidades = instance
            #alunos = Aluno.objects.filter(habilidades__)
            #for usuario in usuarios:
            #    notificacao = Notificacao()
            #    notificacao.tipo = 4  # Cadastro de Vaga
            #    notificacao.vaga = instance
            #    notificacao.usuario = usuario
            #    notificacao.mensagem = NotificacaoMiddleware.TEXTO_NOTIFICACAO_CADASTRO_VAGA % instance.gerente_vaga.nome
            #    notificacao.save()
