# -*- coding: utf-8 -*- 

from django import forms
from django.core.validators import validate_email


class FormularioContato(forms.Form):
    assunto = forms.CharField(max_length=100)
    mensagem = forms.CharField(widget=forms.Textarea)
    seu_email = forms.EmailField(validators=[validate_email])
    copia = forms.BooleanField(required=False, label="Enviar uma cópia para mim")


class LoginForm(forms.ModelForm):
    usuario = forms.CharField(
        max_length=11, label='usuário',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    senha = forms.CharField(
        max_length=11,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})

    )

    class Meta:
        #model = SignUp
        fields = ['usuário', 'senha']

