# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-05-28 15:11
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sva', '0004_auto_20180517_2151'),
    ]

    operations = [
        migrations.AddField(
            model_name='aluno',
            name='curriculo',
            field=models.FileField(blank=True, null=True, upload_to='curriculo/'),
        ),
        migrations.AddField(
            model_name='aluno',
            name='data_upload_curriculo',
            field=models.DateTimeField(null=True, verbose_name='Data de upload'),
        ),
        migrations.AddField(
            model_name='gerentevaga',
            name='situacao',
            field=models.CharField(choices=[('EXCLUIDO', 'Excluído'), ('AGUARDANDO_APROVACAO', 'Aguardando Aprovação'), ('DEFERIDO', 'Deferido'), ('INDEFERIDO', 'Indeferido')], default='AGUARDANDO_APROVACAO', max_length=30, verbose_name='Situação'),
        ),
        migrations.AddField(
            model_name='vaga',
            name='tipo_vaga',
            field=models.IntegerField(choices=[(3, 'Iniciação Científica'), (4, 'Outro'), (1, 'Estágio'), (2, 'Monitoria')], default=4, verbose_name='Tipo da Vaga'),
        ),
        migrations.AlterField(
            model_name='campus',
            name='cidade',
            field=models.CharField(choices=[('BELO HORIZONTE', 'Belo Horizonte'), ('CONTAGEM', 'Contagem'), ('TIMOTEO', 'Timóteo'), ('NEPOMUCENO', 'Nepomuceno'), ('ARAXA', 'Araxá'), ('VARGINHA', 'Varginha'), ('CURVELO', 'Curvelo'), ('DIVINOPOLIS', 'Divinópolis'), ('LEOPOLDINA', 'Leopoldina')], max_length=45),
        ),
        migrations.AlterField(
            model_name='curso',
            name='nivel_ensino',
            field=models.IntegerField(choices=[(5, 'ESPECIALIZACAO'), (1, 'TECNICO'), (4, 'DOUTORADO'), (2, 'GRADUACAO'), (3, 'MESTRADO')], verbose_name='Nível de Ensino'),
        ),
        migrations.AlterField(
            model_name='gerentevaga',
            name='data_aprovacao',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Data de Aprovação'),
        ),
        migrations.AlterField(
            model_name='notificacao',
            name='tipo',
            field=models.PositiveIntegerField(choices=[(5, 'Aprovação de Vaga'), (6, 'Vaga de Interesse'), (2, 'Cadastro de Professor'), (3, 'Cadastro de Empresa'), (4, 'Cadastro de Vaga'), (9, 'Resposta no Fórum'), (7, 'Solicitação de Área de Atuação'), (8, 'Nova Mensagem no Fórum'), (1, 'Indicação de Vaga')], verbose_name='Tipo da Notificação'),
        ),
        migrations.AlterField(
            model_name='vaga',
            name='situacao',
            field=models.IntegerField(choices=[(2, 'Editada'), (4, 'Expirada'), (1, 'Cadastrada'), (3, 'Ativa'), (5, 'Reprovada')], default=1, verbose_name='Situação'),
        ),
        migrations.AlterField(
            model_name='vaga',
            name='usuario_aprovacao',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='vagas_aprovadas', to=settings.AUTH_USER_MODEL),
        ),
    ]
