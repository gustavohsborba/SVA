# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-05-17 21:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sva', '0003_auto_20180509_1220'),
    ]

    operations = [
        migrations.CreateModel(
            name='Avaliacao',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nota', models.IntegerField(verbose_name='Nota atribuída')),
                ('aluno_avaliador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sva.Aluno')),
            ],
        ),
        migrations.AddField(
            model_name='vaga',
            name='cursos',
            field=models.ManyToManyField(blank=True, related_name='vagas_atribuidas', to='sva.Curso'),
        ),
        migrations.AlterField(
            model_name='campus',
            name='cidade',
            field=models.CharField(choices=[('CONTAGEM', 'Contagem'), ('CURVELO', 'Curvelo'), ('NEPOMUCENO', 'Nepomuceno'), ('TIMOTEO', 'Timóteo'), ('LEOPOLDINA', 'Leopoldina'), ('DIVINOPOLIS', 'Divinópolis'), ('ARAXA', 'Araxá'), ('BELO HORIZONTE', 'Belo Horizonte'), ('VARGINHA', 'Varginha')], max_length=45),
        ),
        migrations.AlterField(
            model_name='curso',
            name='nivel_ensino',
            field=models.IntegerField(choices=[(4, 'DOUTORADO'), (3, 'MESTRADO'), (1, 'TECNICO'), (5, 'ESPECIALIZACAO'), (2, 'GRADUACAO')], verbose_name='Nível de Ensino'),
        ),
        migrations.AlterField(
            model_name='notificacao',
            name='tipo',
            field=models.PositiveIntegerField(choices=[(8, 'Nova Mensagem no Fórum'), (2, 'Cadastro de Professor'), (3, 'Cadastro de Empresa'), (5, 'Aprovação de Vaga'), (9, 'Resposta no Fórum'), (6, 'Vaga de Interesse'), (7, 'Solicitação de Área de Atuação'), (1, 'Indicação de Vaga'), (4, 'Cadastro de Vaga')], verbose_name='Tipo da Notificação'),
        ),
        migrations.AlterField(
            model_name='vaga',
            name='situacao',
            field=models.IntegerField(choices=[(1, 'Cadastrada'), (5, 'Reprovada'), (2, 'Editada'), (4, 'Inativa'), (3, 'Ativa')], default=1, verbose_name='Situação'),
        ),
        migrations.AddField(
            model_name='avaliacao',
            name='vaga_avaliada',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sva.Vaga'),
        ),
        migrations.AddField(
            model_name='vaga',
            name='avaliacoes',
            field=models.ManyToManyField(blank=True, related_name='avaliacao_vaga', through='sva.Avaliacao', to='sva.Aluno'),
        ),
    ]