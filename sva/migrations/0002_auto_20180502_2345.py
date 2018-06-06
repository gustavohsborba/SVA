# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-05-02 23:45
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import re
import sva.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sva', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Aluno',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('endereco', models.CharField(max_length=255, null=True)),
                ('matricula', models.CharField(max_length=12, null=True, validators=[django.core.validators.validate_integer])),
                ('cpf', models.CharField(max_length=14, unique=True, validators=[sva.validators.validate_CPF])),
                ('telefone', models.CharField(max_length=20, null=True, validators=[django.core.validators.validate_integer])),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro')),
                ('data_fim', models.DateTimeField(blank=True, null=True, verbose_name='Data de Cancelamento')),
            ],
            options={
                'verbose_name_plural': 'Alunos',
                'verbose_name': 'Aluno',
            },
        ),
        migrations.CreateModel(
            name='AreaAtuacao',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(db_index=True, max_length=45, unique=True)),
                ('area_mae', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='sva.AreaAtuacao')),
            ],
            options={
                'verbose_name_plural': 'Áreas de Atuação',
                'permissions': (('can_request_area_atuacao', 'Pode solicitar área de atuação'), ('can_release_area_atuacao', 'Pode liberar área de atuaçãos')),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nota_media', models.FloatField(default=0.0)),
                ('data_aprovacao', models.DateTimeField(blank=True, null=True, verbose_name='Data de Cadastro')),
                ('data_fim', models.DateTimeField(blank=True, null=True, verbose_name='Data de Cancelamento')),
            ],
            options={
                'verbose_name_plural': 'Gerentes de Vagas',
                'permissions': (('can_request_gerente_vaga', 'Pode solicitar criação de gerente'), ('can_release_gerente_vaga', 'Pode liberar criação de gerente')),
                'verbose_name': 'Gerente de Vagas',
            },
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
                ('tipo', models.PositiveIntegerField(choices=[(3, 'Cadastro de Empresa'), (2, 'Cadastro de Professor'), (6, 'Vaga de Interesse'), (9, 'Resposta no Fórum'), (1, 'Indicação de Vaga'), (8, 'Nova Mensagem no Fórum'), (7, 'Solicitação de Área de Atuação'), (4, 'Cadastro de Vaga'), (5, 'Aprovação de Vaga')], verbose_name='Tipo da Notificação')),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro')),
                ('mensagem', models.TextField()),
                ('lida', models.BooleanField(default=False)),
                ('data_leitura', models.DateTimeField(blank=True, null=True, verbose_name='Data de visualização')),
                ('link', models.CharField(blank=True, max_length=500, null=True)),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notificacoes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'get_latest_by': 'data_cadastro',
                'verbose_name': 'Notificação',
                'verbose_name_plural': 'Notificações',
                'ordering': ['-data_cadastro'],
            },
        ),
        migrations.CreateModel(
            name='Vaga',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(db_index=True, max_length=255, verbose_name='Título')),
                ('descricao', models.TextField(verbose_name='Descrição')),
                ('data_submissao', models.DateTimeField(auto_now_add=True, verbose_name='Data de Submissão')),
                ('data_alteracao', models.DateTimeField(auto_now=True, verbose_name='Data da última alteração')),
                ('data_validade', models.DateTimeField(blank=True, null=True, verbose_name='Data de Validade')),
                ('carga_horaria_semanal', models.PositiveIntegerField(validators=[django.core.validators.RegexValidator(re.compile('^-?\\d+\\Z', 32), code='invalid', message='Enter a valid integer.')], verbose_name='Carga Horária Semanal')),
                ('local', models.CharField(max_length=255, verbose_name='Local de Trabalho')),
                ('valor_bolsa', models.FloatField(verbose_name='Valor da Bolsa')),
                ('beneficios', models.TextField(blank=True, null=True, verbose_name='Benefícios')),
                ('nota_media', models.FloatField(default=0.0, verbose_name='Nota')),
                ('data_aprovacao', models.DateTimeField(blank=True, null=True, verbose_name='Data de Aprovação')),
                ('usuario_aprovacao', models.CharField(blank=True, max_length=60, null=True, verbose_name='Responsável pela aprovação')),
                ('situacao', models.IntegerField(choices=[(2, 'Editada'), (3, 'Ativa'), (5, 'Reprovada'), (4, 'Inativa'), (1, 'Cadastrada')], default=1, verbose_name='Situação')),
                ('alunos_inscritos', models.ManyToManyField(blank=True, related_name='vagas_inscritas', to='sva.Aluno')),
                ('alunos_interessados', models.ManyToManyField(blank=True, related_name='vagas_interesse', to='sva.Aluno')),
                ('areas_atuacao', models.ManyToManyField(related_name='vagas', to='sva.AreaAtuacao')),
            ],
            options={
                'ordering': ['-data_submissao', '-valor_bolsa'],
                'permissions': (('can_evaluate_vaga', 'Pode avaliar vaga'), ('can_recommend_vaga', 'Pode indicar vaga'), ('can_approve_vaga', 'Pode aprovar vaga'), ('can_moderate_vaga', 'Pode moderar o fórum da vaga')),
                'get_latest_by': 'data_submissao',
            },
        ),
        migrations.AlterModelOptions(
            name='campus',
            options={'verbose_name': 'campus', 'verbose_name_plural': 'campi'},
        ),
        migrations.AlterModelOptions(
            name='curso',
            options={'verbose_name': 'Curso', 'verbose_name_plural': 'Cursos'},
        ),
        migrations.AddField(
            model_name='curso',
            name='campus',
            field=models.ManyToManyField(related_name='campi', to='sva.Campus'),
        ),
        migrations.AlterField(
            model_name='campus',
            name='cidade',
            field=models.CharField(choices=[('CONTAGEM', 'Contagem'), ('TIMOTEO', 'Timóteo'), ('VARGINHA', 'Varginha'), ('ARAXA', 'Araxá'), ('NEPOMUCENO', 'Nepomuceno'), ('DIVINOPOLIS', 'Divinópolis'), ('CURVELO', 'Curvelo'), ('LEOPOLDINA', 'Leopoldina'), ('BELO HORIZONTE', 'Belo Horizonte')], max_length=45),
        ),
        migrations.AlterField(
            model_name='curso',
            name='nivel_ensino',
            field=models.IntegerField(choices=[(2, 'GRADUACAO'), (5, 'ESPECIALIZACAO'), (1, 'TECNICO'), (3, 'MESTRADO'), (4, 'DOUTORADO')], verbose_name='Nível de Ensino'),
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
                ('nome', models.CharField(db_index=True, max_length=60)),
            ],
            options={
                'verbose_name_plural': 'Empresas',
                'verbose_name': 'Empresa',
            },
            bases=('sva.gerentevaga',),
        ),
        migrations.CreateModel(
            name='Professor',
            fields=[
                ('gerentevaga_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='sva.GerenteVaga')),
                ('siape', models.CharField(max_length=8, unique=True, validators=[django.core.validators.RegexValidator(re.compile('^-?\\d+\\Z', 32), code='invalid', message='Enter a valid integer.')])),
                ('cpf', models.CharField(max_length=14, unique=True, validators=[sva.validators.validate_CPF])),
                ('curso', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='sva.Curso')),
            ],
            options={
                'verbose_name_plural': 'Professores',
                'verbose_name': 'Professor',
            },
            bases=('sva.gerentevaga',),
        ),
        migrations.AddField(
            model_name='vaga',
            name='gerente_vaga',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vagas', to='sva.GerenteVaga'),
        ),
        migrations.AddField(
            model_name='notificacao',
            name='vaga',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notificacoes', to='sva.Vaga'),
        ),
        migrations.AddField(
            model_name='gerentevaga',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='gerentes_vaga', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='aluno',
            name='areas_atuacao',
            field=models.ManyToManyField(blank=True, related_name='alunos', to='sva.AreaAtuacao'),
        ),
        migrations.AddField(
            model_name='aluno',
            name='curso',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='sva.Curso'),
        ),
        migrations.AddField(
            model_name='aluno',
            name='habilidades',
            field=models.ManyToManyField(blank=True, related_name='alunos', to='sva.Habilidade'),
        ),
        migrations.AddField(
            model_name='aluno',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='alunos', to=settings.AUTH_USER_MODEL),
        ),
    ]
