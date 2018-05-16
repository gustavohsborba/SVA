# -*- coding: utf-8 -*- 

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.auth.admin import UserAdmin
from django.core.validators import validate_email
from .models import *
from django.contrib.auth.forms import AuthenticationForm
import datetime

from .validators import *


class FormularioVaga(forms.ModelForm):

    def clean(self):
        cleaned_data = super(FormularioVaga, self).clean()
        if not cleaned_data['data_validade']:
            cleaned_data['data_validade'] = None
        return cleaned_data

    class Meta:
        model = Vaga
        fields = ('areas_atuacao','titulo','descricao','data_validade','carga_horaria_semanal','local','valor_bolsa','beneficios')

    #data_validade = forms.DateTimeField(widget=forms.SelectDateWidget(),required=False)
    data_validade = forms.CharField(widget=forms.TextInput(attrs={'autocomplete':'off'}), required=False, initial = datetime.datetime.now().strftime('%d/%m/%YT%H:%M'))


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
    Nome_Completo = forms.CharField(max_length=100)
    Rua = forms.CharField(max_length=40)
    Numero = forms.CharField(max_length=4)
    Complemento = forms.CharField(max_length=10,required=False)
    Cidade = forms.CharField(max_length=20)
    Estado = forms.CharField(max_length=20)

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
    Site = forms.CharField(max_length=200)

    class Meta:
        model = Empresa
        fields = ['nome', 'telefone']


class FormularioCadastroEmpresa(forms.ModelForm):
    tipo_formulario = "CADASTRO_EMPRESA"
    cnpj = forms.CharField(max_length=14, validators=[validate_CNPJ])
    password = forms.CharField(widget=forms.PasswordInput(), label='Senha')
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label='Confirmar senha')
    email = forms.EmailField(max_length=40)

    class Meta:
        model = Empresa
        fields = ['cnpj', 'email', 'password', 'confirm_password']

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
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label='Confirmar senha')
    email = forms.EmailField(max_length=40)

    class Meta:
        model = Professor
        fields = ['cpf', 'email', 'siape', 'password', 'confirm_password']

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

