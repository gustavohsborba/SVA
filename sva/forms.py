# -*- coding: utf-8 -*-

from django import forms
from django.core.validators import validate_email
from .models import Vaga


class FormularioCriarVaga(forms.ModelForm):

    class Meta:
        model = Vaga
        fields = ('area_atuacao','titulo','descricao','data_validade','carga_horaria_semanal','local','valor_bolsa','beneficios','gerente_vaga')

class FormularioContato(forms.Form):

    assunto = forms.CharField(max_length=100)
    mensagem = forms.CharField(widget=forms.Textarea)
    seu_email = forms.EmailField(validators=[validate_email])
    copia = forms.BooleanField(required=False, label="Enviar uma cópia para mim")
