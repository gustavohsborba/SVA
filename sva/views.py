# -*- coding: utf-8 -*-

from django.shortcuts import render
from .models import *
from .forms import *
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.forms.utils import ErrorList
# Create your views here.

def pagina_base(request):
    context = {}
    context['cursos'] = Curso.objects.all()
    return render(request, 'sva/base.html', context)

def formulario_contato(request):
    form = FormularioContato()
    return render(request, 'sva/contato.html', {'form': form})


def Login(request):
    if request.user.is_authenticated(): # if user is already logged in
        return HttpResponseRedirect('/') # SHOULD BE DASHBOARD

    if request.method == "POST":
        user = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=user, password=password)
        if user is not None:
            if user.is_authenticated:
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                messages.error(request, 'Usuário ou senha inválido')
                return HttpResponseRedirect('')
        else:
            messages.error(request, 'Usuário ou senha inválido')
            return HttpResponseRedirect('')

    return render(request, 'registration/login_template.html', {})

def Logout(request):
    logout(request)
    return HttpResponseRedirect('/')

def RecuperarSenha(request):
    if request.method == "POST":
        user = request.POST['cpf']
        password = request.POST['senha']

        user ={}
        if user is not None:
            if user.is_authenticated:
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                messages.error(request, 'Combinação de usuário e senha invalida')
                return HttpResponseRedirect('')
        else:
            messages.error(request, 'Combinação de usuário e senha invalida')
            return HttpResponseRedirect('')
    return render(request, 'registration/recuperarSenha.html', {})

