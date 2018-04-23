# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-22 23:33
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.auth.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import re
import sva.validators


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
        ('admin', '0002_logentry_remove_auto_add'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sva', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Aluno',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('cpf', models.CharField(max_length=14, unique=True, validators=[sva.validators.validate_CPF])),
                ('telefone', models.CharField(max_length=20, null=True, validators=[django.core.validators.validate_integer])),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro')),
                ('data_fim', models.DateTimeField(blank=True, null=True, verbose_name='Data de Cancelamento')),
            ],
            options={
                'abstract': False,
                'verbose_name_plural': 'users',
                'verbose_name': 'user',
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='AreaAtuacao',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(db_index=True, max_length=45, unique=True)),
            ],
            options={
                'verbose_name_plural': 'Áreas de Atuação',
                'verbose_name': 'Área de Atuação',
            },
        ),
        migrations.CreateModel(
            name='FiltroPesquisa',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255, verbose_name='Nome do Filtro')),
                ('chave', models.CharField(max_length=255)),
                ('valor', models.CharField(max_length=255)),
                ('aluno', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='filtros_pesquisa', to='sva.Aluno')),
            ],
            options={
                'verbose_name_plural': 'Filtros de Pesquisa',
                'verbose_name': 'Filtro de Pesquisa',
            },
        ),
        migrations.CreateModel(
            name='GerenteVaga',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('nome', models.CharField(db_index=True, max_length=60)),
                ('nota_media', models.FloatField(default=0.0)),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro')),
                ('data_fim', models.DateTimeField(blank=True, null=True, verbose_name='Data de Cancelamento')),
            ],
            options={
                'verbose_name_plural': 'Gerentes de Vagas',
                'verbose_name': 'Gerente de Vagas',
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Habilidade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(db_index=True, max_length=45, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Notificacao',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.PositiveIntegerField(choices=[(7, 'Solicitação de Área de Atuação'), (1, 'Indicação de Vaga'), (2, 'Cadastro de Professor'), (9, 'Resposta no Fórum'), (3, 'Cadastro de Empresa'), (5, 'Aprovação de Vaga'), (6, 'Vaga de Interesse'), (4, 'Cadastro de Vaga'), (8, 'Nova Mensagem no Fórum')], verbose_name='Tipo da Notificação')),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro')),
                ('mensagem', models.TextField()),
                ('aluno', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notificacoes', to='sva.Aluno')),
            ],
            options={
                'verbose_name_plural': 'Notificações',
                'ordering': ['-data_cadastro'],
                'get_latest_by': 'data_cadastro',
                'verbose_name': 'Notificação',
            },
        ),
        migrations.CreateModel(
            name='Professor',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('siape', models.CharField(max_length=8, unique=True, validators=[django.core.validators.RegexValidator(re.compile('^-?\\d+\\Z', 32), code='invalid', message='Enter a valid integer.')])),
                ('cpf', models.CharField(max_length=14, unique=True, validators=[sva.validators.validate_CPF])),
            ],
            options={
                'verbose_name_plural': 'Professores',
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Vaga',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(db_index=True, max_length=255, verbose_name='Título')),
                ('descricao', models.TextField(verbose_name='Descrição')),
                ('data_submissao', models.DateTimeField(auto_now_add=True, verbose_name='Data de Submissão')),
                ('data_validade', models.DateTimeField(blank=True, null=True, verbose_name='Data de Validade')),
                ('carga_horaria_semanal', models.PositiveIntegerField(validators=[django.core.validators.RegexValidator(re.compile('^-?\\d+\\Z', 32), code='invalid', message='Enter a valid integer.')], verbose_name='Carga Horária Semanal')),
                ('local', models.CharField(max_length=255, verbose_name='Local de Trabalho')),
                ('valor_bolsa', models.FloatField(verbose_name='Valor da Bolsa')),
                ('beneficios', models.TextField(blank=True, null=True, verbose_name='Benefícios')),
                ('nota_media', models.FloatField(default=0.0, verbose_name='Nota')),
            ],
            options={
                'permissions': (('can_evaluate_vaga', 'Pode avaliar vaga'), ('can_recommend_vaga', 'Pode indicar vaga'), ('can_approve_vaga', 'Pode aprovar vaga'), ('can_moderate_vaga', 'Pode moderar o fórum da vaga')),
                'ordering': ['-data_submissao', '-valor_bolsa'],
                'get_latest_by': 'data_submissao',
            },
        ),
        migrations.RemoveField(
            model_name='perfil',
            name='curso',
        ),
        migrations.RemoveField(
            model_name='perfil',
            name='user',
        ),
        migrations.AddField(
            model_name='curso',
            name='campus',
            field=models.ManyToManyField(related_name='campi', to='sva.Campus'),
        ),
        migrations.AlterField(
            model_name='campus',
            name='cidade',
            field=models.CharField(choices=[('NEPOMUCENO', 'Nepomuceno'), ('BELO HORIZONTE', 'Belo Horizonte'), ('DIVINOPOLIS', 'Divinópolis'), ('CURVELO', 'Curvelo'), ('TIMOTEO', 'Timóteo'), ('VARGINHA', 'Varginha'), ('LEOPOLDINA', 'Leopoldina'), ('CONTAGEM', 'Contagem'), ('ARAXA', 'Araxá')], max_length=45),
        ),
        migrations.AlterField(
            model_name='curso',
            name='nivel_ensino',
            field=models.IntegerField(choices=[(5, 'ESPECIALIZACAO'), (2, 'GRADUACAO'), (4, 'DOUTORADO'), (1, 'TECNICO'), (3, 'MESTRADO')], verbose_name='Nível de Ensino'),
        ),
        migrations.AlterField(
            model_name='curso',
            name='nome',
            field=models.CharField(max_length=45, unique=True),
        ),
        migrations.CreateModel(
            name='Empresa',
            fields=[
                ('gerentevaga_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='sva.GerenteVaga')),
                ('cnpj', models.CharField(max_length=14, unique=True, validators=[sva.validators.validate_CNPJ])),
            ],
            options={
                'abstract': False,
                'verbose_name_plural': 'users',
                'verbose_name': 'user',
            },
            bases=('sva.gerentevaga',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.DeleteModel(
            name='Perfil',
        ),
        migrations.AddField(
            model_name='vaga',
            name='Gerente_vaga',
            field=models.ManyToManyField(related_name='vagas', to='sva.GerenteVaga'),
        ),
        migrations.AddField(
            model_name='vaga',
            name='area_atuacao',
            field=models.ManyToManyField(related_name='vagas', to='sva.AreaAtuacao'),
        ),
        migrations.AddField(
            model_name='professor',
            name='curso',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='sva.Curso'),
        ),
        migrations.AddField(
            model_name='notificacao',
            name='gerente_vagas',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='gerentes', to='sva.GerenteVaga'),
        ),
        migrations.AddField(
            model_name='notificacao',
            name='vaga',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notificacoes', to='sva.Vaga'),
        ),
        migrations.AddField(
            model_name='gerentevaga',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gerentes_vaga', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='aluno',
            name='curso',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sva.Curso'),
        ),
        migrations.AddField(
            model_name='aluno',
            name='habilidades',
            field=models.ManyToManyField(related_name='alunos', to='sva.Habilidade'),
        ),
        migrations.AddField(
            model_name='aluno',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alunos', to=settings.AUTH_USER_MODEL),
        ),
    ]
