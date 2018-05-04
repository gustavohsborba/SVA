# -*- coding: utf-8 -*- 

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.core.validators import validate_email
from .models import *
from django.contrib.auth.forms import AuthenticationForm

from .validators import *


class FormularioVaga(forms.ModelForm):

    class Meta:
        model = Vaga
        fields = ('areas_atuacao','titulo','descricao','data_validade','carga_horaria_semanal','local','valor_bolsa','beneficios')


class FormularioContato(forms.Form):

    assunto = forms.CharField(max_length=100)
    mensagem = forms.CharField(widget=forms.Textarea)
    seu_email = forms.EmailField(validators=[validate_email])
    copia = forms.BooleanField(required=False, label="Enviar uma cópia para mim")


class FormularioCadastroAluno(forms.ModelForm):
    first_name = forms.CharField(max_length=50,label='Primeiro Nome')
    password = forms.CharField(widget=forms.PasswordInput(), label='Senha')
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label='Confirmar senha')
    email = forms.CharField(max_length=30, validators=[validate_email])

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


class FormularioCadastroEmpresa(forms.models.BaseForm):
    pass


class FormularioCadastroProfessor(forms.models.BaseForm):
    pass


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

