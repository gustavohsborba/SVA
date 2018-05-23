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
        fields = ('cursos','areas_atuacao','titulo','descricao','data_validade','carga_horaria_semanal','local','valor_bolsa','beneficios')

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
    first_name = forms.CharField(max_length=50,label='Nome Completo')
    password = forms.CharField(widget=forms.PasswordInput(), label='Senha')
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label='Confirmar senha')
    email = forms.EmailField(max_length=40)

    class Meta:
        model = Aluno
        fields = ['cpf','first_name', 'email', 'curso', 'password', 'confirm_password']

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
    Numero = forms.CharField(max_length=4,widget=forms.TextInput(attrs={"class":"form-control form-control-lg"}))
    Complemento = forms.CharField(max_length=10,required=False,widget=forms.TextInput(attrs={"class":"form-control form-control-lg"}))
    Cidade = forms.CharField(max_length=20,widget=forms.TextInput(attrs={"class":"form-control form-control-lg"}))
    Estado = forms.CharField(max_length=20,widget=forms.TextInput(attrs={"class":"form-control form-control-lg"}))
    matricula = forms.CharField(max_length=12, widget=forms.TextInput(attrs={"class": "form-control form-control-lg"}))
    telefone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={"class": "form-control form-control-lg"}))
    curso = forms.ModelChoiceField(queryset=Curso.objects.all(),widget=forms.Select(attrs={"class":"form-control form-control-lg"}))

    def __init__(self, *args, **kwargs):
        super(FormularioEditarAluno, self).__init__(*args, **kwargs)
        self.fields['habilidades'].widget.attrs['class'] = 'form-control'
    class Meta:
        model = Aluno
        fields = ['curso', 'matricula', 'telefone' ,'habilidades']


class FormularioEditarEmpresa(forms.ModelForm):
    Bairro = forms.CharField(max_length=40)
    Rua = forms.CharField(max_length=40)
    Numero = forms.CharField(max_length=4)
    Complemento = forms.CharField(max_length=10, required=False)
    Cidade = forms.CharField(max_length=20)
    Estado = forms.CharField(max_length=20)
    Email = forms.CharField(max_length=100, validators=[validate_email])
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
    Telefone = forms.CharField(max_length=12)

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

class FormularioPesquisaVagasAluno(forms.Form):
    Vaga_Cadastrada = forms.CharField(max_length=50,required=False,widget=forms.TextInput(attrs={'placeholder': 'Vaga','class':'form-control'}))
    Area_Atuacao = forms.CharField(max_length=50,required=False,widget=forms.TextInput(attrs={'placeholder': 'Area de Atuação','class':'form-control'}))

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