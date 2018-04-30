# -*- coding: utf-8 -*- 

from django import forms
from django.core.validators import validate_email
from .models import Vaga
from django.contrib.auth.forms import AuthenticationForm

from .validators import *

class FormularioCriarVaga(forms.ModelForm):

    class Meta:
        model = Vaga
        fields = ('area_atuacao','titulo','descricao','data_validade','carga_horaria_semanal','local','valor_bolsa','beneficios','gerente_vaga')

class FormularioContato(forms.Form):

    assunto = forms.CharField(max_length=100)
    mensagem = forms.CharField(widget=forms.Textarea)
    seu_email = forms.EmailField(validators=[validate_email])
    copia = forms.BooleanField(required=False, label="Enviar uma cópia para mim")


class FormularioCadastroAluno(forms.models.BaseForm):
    pass


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

