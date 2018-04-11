
from django import forms
from django.contrib.auth.models import User
from django.core.validators import validate_email

from .models import Perfil


class FormularioContato(forms.Form):
    assunto = forms.CharField(max_length=100)
    mensagem = forms.CharField(widget=forms.Textarea)
    seu_email = forms.EmailField(validators=[validate_email])
    copia = forms.BooleanField(required=False, label="Enviar uma cópia para mim")



class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ('telefone', 'curso')