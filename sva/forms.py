# -*- coding: utf-8 -*- 

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.auth.admin import UserAdmin
from django.core.validators import validate_email

from .models import *
from django.contrib.auth.forms import AuthenticationForm
import datetime
from table import Table
from table.columns import Column

from .validators import *

class FormularioVaga(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(FormularioVaga, self).__init__(*args, **kwargs)
        self.fields['cursos'].widget.attrs['class'] = 'form-control'
        self.fields['areas_atuacao'].widget.attrs['class'] = 'form-control'
        self.fields['descricao'].widget.attrs['class'] = 'form-control'
        self.fields['descricao'].widget.attrs['rows'] = '3'
        self.fields['descricao'].widget.attrs['placeholder'] = 'Descrição básica'
        self.fields['valor_bolsa'].widget.attrs['min'] = '0'
        self.fields['valor_bolsa'].widget.attrs['class'] = 'form-control'
        self.fields['valor_bolsa'].widget.attrs['placeholder'] = '000,00'
        self.fields['carga_horaria_semanal'].widget.attrs['class'] = 'form-control'
        self.fields['carga_horaria_semanal'].widget.attrs['placeholder'] = '0'
        self.fields['beneficios'].widget.attrs['class'] = 'form-control'
        self.fields['beneficios'].widget.attrs['rows'] = '5'
        self.fields['beneficios'].widget.attrs['placeholder'] = 'Benefícios concedidos (opcional)'

    def clean(self):
        cleaned_data = super(FormularioVaga, self).clean()
        if not cleaned_data['data_validade']:
            cleaned_data['data_validade'] = None
        return cleaned_data

    class Meta:
        model = Vaga
        fields = ('cursos','areas_atuacao','titulo','descricao','data_validade','carga_horaria_semanal','local','valor_bolsa','beneficios','tipo_vaga')

    data_validade = forms.CharField(widget=forms.TextInput(attrs={'autocomplete':'off'}), required=False)

class FormularioGerenciaVaga(forms.Form):
    vaga_nome = forms.CharField(max_length=50,required=False,widget=forms.TextInput(attrs={'placeholder': 'Procurar vagas','class':'form-control'}))

class FormularioContato(forms.Form):

    assunto = forms.CharField(max_length=100)
    mensagem = forms.CharField(widget=forms.Textarea)
    seu_email = forms.EmailField(validators=[validate_email])
    copia = forms.BooleanField(required=False, label="Enviar uma cópia para mim")


class FormularioCadastroAluno(forms.ModelForm):
    tipo_formulario = "CADASTRO_ALUNO"
    name = forms.CharField(max_length=50,label='Nome Completo')
    password = forms.CharField(widget=forms.PasswordInput(), label='Senha')
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label='Confirmar senha')
    email = forms.EmailField(max_length=40)

    class Meta:
        model = Aluno
        fields = ['cpf','name', 'email', 'curso', 'password', 'confirm_password']

    def clean(self):
        cleaned_data = super(FormularioCadastroAluno, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError(
                "Senha e Confirmar senha são diferentes"
            )


class FormularioEditarAluno(forms.ModelForm):

    Nome_Completo = forms.CharField(max_length=100,widget=forms.TextInput(attrs={"class":"form-control form-control-lg"}))
    Rua = forms.CharField(max_length=40,widget=forms.TextInput(attrs={"class":"form-control form-control-lg"}))
    Numero = forms.CharField(max_length=6,widget=forms.TextInput(attrs={"class":"form-control form-control-lg"}))
    Complemento = forms.CharField(max_length=50,required=False,widget=forms.TextInput(attrs={"class":"form-control form-control-lg"}))
    Cidade = forms.CharField(max_length=30,widget=forms.TextInput(attrs={"class":"form-control form-control-lg"}))
    Estado = forms.CharField(max_length=25,widget=forms.TextInput(attrs={"class":"form-control form-control-lg"}))
    matricula = forms.CharField(max_length=12, widget=forms.TextInput(attrs={"class": "form-control form-control-lg", "placeholder": "Número de matrícula"}))
    telefone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={"class": "form-control form-control-lg", "placeholder": "Número de contato"}))
    curso = forms.ModelChoiceField(queryset=Curso.objects.all(),widget=forms.Select(attrs={"class":"form-control form-control-lg"}))
    Email = forms.CharField(max_length=100, widget=forms.TextInput(attrs={"class": "form-control form-control-lg"}))

    def __init__(self, *args, **kwargs):
        super(FormularioEditarAluno, self).__init__(*args, **kwargs)
        self.fields['habilidades'].widget.attrs['class'] = 'form-control'
    class Meta:
        model = Aluno
        fields = ['curso', 'matricula', 'telefone', 'habilidades']


class FormularioEditarEmpresa(forms.ModelForm):
    Bairro = forms.CharField(max_length=30)
    Rua = forms.CharField(max_length=40)
    Numero = forms.CharField(max_length=6)
    Complemento = forms.CharField(max_length=50, required=False)
    Cidade = forms.CharField(max_length=30)
    Estado = forms.CharField(max_length=25)
    Email = forms.CharField(max_length=100, validators=[validate_email])
    telefone = forms.CharField(max_length=12, min_length=9, validators=[validate_integer], help_text='apenas números')
    Site = forms.CharField(max_length=200, required=False)

    class Meta:
        model = Empresa
        fields = ['nome', 'telefone']


class FormularioCadastroEmpresa(forms.ModelForm):
    tipo_formulario = "CADASTRO_EMPRESA"
    cnpj = forms.CharField(max_length=14, validators=[validate_CNPJ])
    nome = forms.CharField(max_length=60, label="Nome da Empresa")
    password = forms.CharField(widget=forms.PasswordInput(), label='Senha')
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label='Confirmar senha')
    email = forms.EmailField(max_length=40)

    class Meta:
        model = Empresa
        fields = ['cnpj', 'nome', 'email', 'password', 'confirm_password']

    def clean(self):
        cleaned_data = super(FormularioCadastroEmpresa, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError(
                "Senha e Confirmar senha são diferentes"
            )


class FormularioCadastroProfessor(forms.ModelForm):
    tipo_formulario = "CADASTRO_PROFESSOR"
    password = forms.CharField(widget=forms.PasswordInput(), label='Senha')
    nome = forms.CharField(max_length=60, label="Nome")
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label='Confirmar senha')
    email = forms.EmailField(max_length=40)

    class Meta:
        model = Professor
        fields = ['cpf', 'nome', 'email', 'siape', 'curso', 'password', 'confirm_password']

    def clean(self):
        cleaned_data = super(FormularioCadastroProfessor, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError(
                "Senha e Confirmar senha são diferentes"
            )


class FormularioEditarProfessor(forms.ModelForm):
    Nome_Completo = forms.CharField(max_length=100)
    telefone = forms.CharField(min_length=9, required=False)
    Email = forms.CharField(max_length=100, validators=[validate_email])
    curso = forms.ModelChoiceField(queryset=Curso.objects.all(), widget=forms.Select(attrs={"class": "form-control form-control-lg"}))

    class Meta:
        model = Professor
        fields = ['curso', 'siape']


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=11, label='usuário',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        max_length=11,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})

    )

    class Meta:
        #model = SignUp
        fields = ['usuário', 'senha']

class FormularioPesquisarVagas(forms.Form):
    def is_valid(self):
        return True
    #NAO MUDAR O NOME DOS CAMPOS!!!
    curso_1 = forms.ModelMultipleChoiceField(queryset=Curso.objects.all(), widget=forms.Select(attrs={"class": "form-control form-control-lg","style": "display: none;", "name":"curso"}))
    area_1 = forms.ModelMultipleChoiceField(queryset=AreaAtuacao.objects.all(), widget=forms.Select(
        attrs={"class": "form-control form-control-lg", "style": "display: none;", "name": "area"}))


class FormularioPesquisaVagasAluno(forms.Form):
    Vaga_Cadastrada = forms.CharField(max_length=50,required=False,widget=forms.TextInput(attrs={'placeholder': 'Vaga','class':'form-control'}))
    Area_Atuacao = forms.CharField(max_length=50,required=False,widget=forms.TextInput(attrs={'placeholder': 'Area de Atuação','class':'form-control'}))


class FormularioPesquisaProfessor(forms.Form):
    curso_campus_nome = forms.CharField(max_length=50, required=False, widget=forms.TextInput(
        attrs={'placeholder': 'Pesquisar por curso, campus ou Nome',
               'class': 'form-control col-sm-6 col-md-6', 'size': '40%'}))


class FormularioPesquisaEmpresa(forms.Form):
    nome = forms.CharField(max_length=50, required=False, widget=forms.TextInput(
        attrs={'placeholder': 'Filtrar por nome da empresa',
               'class': 'form-control col-sm-6 col-md-6', 'size': '40%'}))


class FormularioAprovacao(forms.Form):
    aprovado = forms.CharField(max_length=15, required=True, widget=forms.HiddenInput(attrs={"class": "form-control"}), validators=[validate_boolean])
    justificativa = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": 'Insira uma justificativa'}),
                                    required=True, help_text='Por favor, insira uma justificativa ou uma mensagem de boas-vindas, que será enviada para o usuário ')


# TODO: https://github.com/shymonk/django-datatable
class ProfessorTable(Table):
    CPF = Column(field='cpf', searchable=True, sortable=True)
    Nome = Column(field='user.first_name', searchable=True, sortable=True)
    SIAPE = Column(field='siape', searchable=True, sortable=True)
    Curso = Column(field='curso', searchable=True, sortable=True)
    Data_Cadastro = Column(field='user.date_joined', searchable=False, sortable=False)
    Data_Aprovacao = Column(field='data_aprovacao', searchable=False, sortable=False)
    class Meta:
        model = Professor


class UploadCurriculo(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = ['curriculo']

    def __init__(self, *args, **kwargs):
        super(UploadCurriculo, self).__init__(*args, **kwargs)
        self.fields['curriculo'].widget.attrs['accept'] = '.pdf'
        self.fields['curriculo'].widget.attrs['id'] = 'files-input-upload'
        self.fields['curriculo'].widget.attrs['class'] = 'input-file'
        self.fields['curriculo'].widget.attrs['data-max-size'] = '32154'

class IndicarVaga(forms.Form):
    email = forms.EmailField(required=True,max_length=50,widget=forms.EmailInput(attrs={'class':'form-control form-control-lg','placeholder':'Digite um email..','id':'email' }))