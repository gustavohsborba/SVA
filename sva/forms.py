# -*- coding: utf-8 -*- 

from django import forms
from django.core.validators import validate_email
from sva.models import Aluno


class FormularioContato(forms.Form):
    assunto = forms.CharField(max_length=100)
    mensagem = forms.CharField(widget=forms.Textarea)
    seu_email = forms.EmailField(validators=[validate_email])
    copia = forms.BooleanField(required=False, label="Enviar uma cópia para mim")

class FormularioCadastroAluno(forms.ModelForm):

    class Meta:
        model = Aluno
        fields = ['cpf', 'email', 'password']
