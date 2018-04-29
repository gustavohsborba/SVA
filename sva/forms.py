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
    password = forms.CharField(widget=forms.PasswordInput(),label='Senha')
    confirm_password = forms.CharField(widget=forms.PasswordInput(),label='Confirmar senha')
    class Meta:
        model = Aluno
        fields = ['cpf', 'email', 'curso', 'password']

    def clean(self):
        cleaned_data = super(FormularioCadastroAluno, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError(
                "Senha e Confirmar senha são diferentes"
            )