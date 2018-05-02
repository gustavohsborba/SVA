# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-29 22:38
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sva', '0002_auto_20180425_1020'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='aluno',
            options={'verbose_name': 'Aluno', 'verbose_name_plural': 'Alunos'},
        ),
        migrations.AddField(
            model_name='aluno',
            name='endereco',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='aluno',
            name='matricula',
            field=models.CharField(max_length=12, null=True, validators=[django.core.validators.validate_integer]),
        ),
        migrations.AlterField(
            model_name='campus',
            name='cidade',
            field=models.CharField(choices=[('ARAXA', 'Araxá'), ('TIMOTEO', 'Timóteo'), ('DIVINOPOLIS', 'Divinópolis'), ('BELO HORIZONTE', 'Belo Horizonte'), ('NEPOMUCENO', 'Nepomuceno'), ('CONTAGEM', 'Contagem'), ('VARGINHA', 'Varginha'), ('LEOPOLDINA', 'Leopoldina'), ('CURVELO', 'Curvelo')], max_length=45),
        ),
        migrations.AlterField(
            model_name='curso',
            name='nivel_ensino',
            field=models.IntegerField(choices=[(4, 'DOUTORADO'), (5, 'ESPECIALIZACAO'), (2, 'GRADUACAO'), (1, 'TECNICO'), (3, 'MESTRADO')], verbose_name='Nível de Ensino'),
        ),
        migrations.AlterField(
            model_name='notificacao',
            name='tipo',
            field=models.PositiveIntegerField(choices=[(3, 'Cadastro de Empresa'), (7, 'Solicitação de Área de Atuação'), (2, 'Cadastro de Professor'), (8, 'Nova Mensagem no Fórum'), (1, 'Indicação de Vaga'), (9, 'Resposta no Fórum'), (5, 'Aprovação de Vaga'), (4, 'Cadastro de Vaga'), (6, 'Vaga de Interesse')], verbose_name='Tipo da Notificação'),
        ),
    ]