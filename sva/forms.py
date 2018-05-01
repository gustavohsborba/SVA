# -*- coding: utf-8 -*- 

from django import forms
from django.core.validators import validate_email



class FormularioContato(forms.Form):
    assunto = forms.CharField(max_length=100)
    mensagem = forms.CharField(widget=forms.Textarea)
    seu_email = forms.EmailField(validators=[validate_email])
