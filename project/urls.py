"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function viewsog
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
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf.urls.i18n import i18n_patterns
from sva.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^$', home),
    url(r'^home', home),
    url(r'^layout', layout),

    url(r'^accounts/password_change/$', alterar_senha, name='alterarsenha'),
    url(r'^accounts/recuperar_senha/$', recuperar_senha, name='recuperarsenha'),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^contato', formulario_contato),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),

    url(r'^cadastro/', cadastro, name='cadastro'),
    url(r'^cadastroaluno/$', cadastrar_aluno, name='Cadastro_Aluno'),
    url(r'^cadastroprofessor/$', cadastrar_professor, name='Cadastro_Professor'),
    url(r'^cadastroempresa/$', cadastrar_empresa, name='Cadastro_Empresa'),

    url(r'^vagas/$', principal_vaga, name='vaga_principal'),
    url(r'^vagas/(?P<pkvaga>\d+)$', visualizar_vaga, name='vaga_visualizar'),
    url(r'^vagas/comentario/(?P<pkvaga>\d+)/$', adicionar_comentario, name='comentario'),
    url(r'^vagas/gerenciar/$', gerenciar_vaga, name='vaga_gerenciar'),
    url(r'^vagas/editar/(?P<pkvaga>\d+)$', editar_vaga, name='vaga_editar'),
    url(r'^vagas/editar/(?P<pkvaga>\d+)/encerrar$', encerrar_inscricao_vaga),
    url(r'^vagas/inscritos/(?P<pkvaga>\d+)$', lista_alunos_vaga, name='vaga_listar'),
    url(r'^vagas/criar/$', criar_vaga, name='vaga_criar'),
    url(r'^vagas/pendentes/$', gerenciar_vaga_pendente, name='vaga_gerenciar_pendentes'),
    url(r'^vagas/(?P<pkvaga>\d+)/aprovar$', aprovar_vaga, name='vaga_aprovar'),
    url(r'^vagas/pesquisar/$', pesquisar_vaga, name='vaga_pesquisar'),

    url(r'^aluno/editar/(?P<pk>\d+)$', editar_aluno, name='Editar_Aluno'),
    url(r'^aluno/editar/desativar/(?P<pk>\d+)$', excluir_aluno, name='Excluir_Aluno'),
    url(r'^aluno/perfil/(?P<pk>\d+)', exibir_aluno, name='Exibir_Aluno'),
    url(r'^aluno/vagas/(?P<pk>\d+)$', Listar_Vagas_Aluno, name='Listar_Vagas_Aluno'),
    url(r'^aluno/curriculo/(?P<pk>\d+)$', upload_curriculo, name='upload_curriculo'),
    url(r'^aluno/curriculo/excluir/(?P<pk>\d+)$', excluir_curriculo, name='excluir_curriculo'),
    url(r'^aluno/curriculo/download/(?P<pk>\d+)$', download_curriculo, name='download_curriculo'),

    url(r'^professor/listar/$', listar_professor, name='Listar_Professor'),
    url(r'^professor/gerenciar/$', liberar_cadastro_professores_lista, name='Gerenciar_Professor'),
    url(r'^professor/editar/(?P<pk>\d+)$', editar_professor, name='Editar_Professor'),
    url(r'^professor/editar/(?P<pk>\d+)/excluir$', excluir_professor, name='Excluir_Professor'),
    url(r'^professor/perfil/(?P<pk>\d+)$', exibir_professor, name='Exibir_Professor'),
    url(r'^professor/perfil/(?P<pk>\d+)/aprovar_cadastro$', aprovar_cadastro_professor, name='Aprovar_Professor'),

    url(r'^empresa/gerenciar/$', liberar_cadastro_empresas_lista, name='Gerenciar_Empresas'),
    url(r'^empresa/listar/$', listar_empresa, name='Listar_Empresa'),
    url(r'^empresa/editar/(?P<pk>\d+)$', editar_empresa, name='Editar_Empresa'),
    url(r'^empresa/editar/(?P<pk>\d+)/excluir$', excluir_empresa, name='Excluir_Empresa'),
    url(r'^empresa/perfil/(?P<pk>\d+)$', exibir_empresa, name='Exibir_Empresa'),
    url(r'^empresa/perfil/(?P<pk>\d+)/aprovar_cadastro$', aprovar_cadastro_empresa, name='Aprovar_Empresa'),

    url(r'^notificacoes/visualizar', acessar_notificacao, name='notificacao_visualizar'),
    url(r'^ratings/', include('star_ratings.urls', namespace='ratings', app_name='ratings')),

    url(r'^comentario/excluir/(?P<pkcomentario>\d+)$', excluir_comentario, name='excluir_comentario'),

    url(r'^areaatuacao_gerenciar/$', gerenciar_areaatuacao, name='gerenciar_areaatuacao'),
] + static(settings.STATIC_URL, document_root= settings.STATIC_ROOT)


urlpatterns += i18n_patterns(
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)