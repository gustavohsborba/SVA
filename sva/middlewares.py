from datetime import timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

from .models import *

class NotificacaoMiddleware:

    TEXTO_NOTIFICACAO_CADASTRO_PROFESSOR = 'O professor %s se cadastrou no sistema. Clique aqui para moderar o acesso'
    TEXTO_NOTIFICACAO_CADASTRO_EMPRESA = 'A empresa %s deseja acessar o SVA. Clique aqui para liberar ou negar o acesso'

    TEXTO_NOTIFICACAO_INDICACAO_VAGA = '%s indicou a vaga %s pra você. Clique para visualizar'
    TEXTO_NOTIFICACAO_CADASTRO_VAGA = '%s cadastrou uma nova vaga. Clique para visualizar'
    TEXTO_NOTIFICACAO_APROVACAO_VAGA = '%s cadastrou uma nova vaga. Clique para visualizar'

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
                notificacao.mensagem = NotificacaoMiddleware.TEXTO_NOTIFICACAO_CADASTRO_VAGA % instance.gerente_vaga.nome
                notificacao.save()


    @receiver(post_save, sender=Empresa)
    def cria_notificacao_cadastro_empresa(selfsender, instance, created, **kwargs):
        if created:
            grupos = Group.objects.filter(name__in=['Administrador', 'Setor de Estágios'])
            usuarios = User.objects.filter(groups__in=grupos)
            for usuario in usuarios:
                notificacao = Notificacao()
                notificacao.tipo = Notificacao.TIPO_CADASTRO_EMPRESA
                notificacao.vaga = None
                notificacao.usuario = usuario
                notificacao.mensagem = NotificacaoMiddleware.TEXTO_NOTIFICACAO_CADASTRO_EMPRESA % instance.nome
                notificacao.link = reverse("Exibir_Empresa", {'pk': instance.pk})
                notificacao.save()

    @receiver(post_save, sender=Professor)
    def cria_notificacao_cadastro_Professor(selfsender, instance, created, **kwargs):
        if created:
            grupos = Group.objects.filter(name__in=['Administrador', 'Setor de Estágios'])
            usuarios = User.objects.filter(groups__in=grupos)
            for usuario in usuarios:
                notificacao = Notificacao()
                notificacao.tipo = Notificacao.TIPO_CADASTRO_PROFESSOR
                notificacao.vaga = None
                notificacao.usuario = usuario
                notificacao.mensagem = NotificacaoMiddleware.TEXTO_NOTIFICACAO_CADASTRO_PROFESSOR % instance.user.nome
                notificacao.link = reverse("Exibir_Empresa", {'pk': instance.pk})
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
