"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from sva.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^$', home),
    url(r'^home', home),
    url(r'^accounts/password_change/$', recuperar_senha, name='recuperarsenha'),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^cadastro/', cadastro, name='cadastro'),
    url(r'^contato', formulario_contato),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^vagas/$', principal_vaga, name='vaga_principal'),
    url(r'^vagas/gerenciar/$', gerenciar_vaga, name='vaga_gerenciar'),
    url(r'^vagas/editar/(?P<pkvaga>\d+)$', editar_vaga, name='vaga_editar'),
    url(r'^vagas/(?P<pkvaga>\d+)$', visualizar_vaga, name='vaga_visualizar'),
    url(r'^vagas/editar/(?P<pkvaga>\d+)/encerrar$', encerrar_inscricao_vaga),
    url(r'^vagas/listar_alunos/(?P<pkvaga>\d+)$', lista_alunos_vaga, name='vaga_listar'),
    url(r'^vagas/criar/$', criar_vaga, name='vaga_criar'),
    url(r'^cadastroaluno/$', cadastrar_aluno, name='Cadastro_Aluno'),
    url(r'^aluno/editaraluno/(?P<pk>\d+)$', editar_aluno, name='Editar_Aluno'),
    url(r'^aluno/editaraluno/(?P<pk>\d+)/excluir$', excluir_aluno, name='Excluir_Aluno'),
    url(r'^aluno/perfil/(?P<pk>\d+)', exibir_aluno, name='Exibir_Aluno'),
    url(r'^layout', layout),

] + static(settings.STATIC_URL, document_root= settings.STATIC_ROOT)


urlpatterns += i18n_patterns(
    url(r'^admin/', include(admin.site.urls)),
)
