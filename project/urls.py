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
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from sva.views import *

urlpatterns = [
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^home', pagina_base),
    url(r'^contato', formulario_contato),
    url(r'^vagas/$', PrincipalVaga, name='vaga_principal'),
    url(r'^vagas/gerenciar/$', GerenciarVaga, name='vaga_gerenciar'),
    url(r'^vagas/editar/(?P<pkvaga>\d+)$', EditarVaga, name='vaga_editar'),
    url(r'^vagas/criar/$', CriarVaga, name='vaga_criar')
]

urlpatterns += i18n_patterns(
    url(r'^admin/', include(admin.site.urls)),
)
