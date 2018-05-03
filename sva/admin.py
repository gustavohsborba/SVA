from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from sva.models import *

# Register your models here.
admin.site.register(Aluno)
admin.site.register(Empresa)
admin.site.register(Professor)
admin.site.register(AreaAtuacao)
admin.site.register(Habilidade)


@admin.register(Campus)
class CampusAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        if obj and Curso.objects.filter(campus=obj):
            return False
        return True


@admin.register(Curso)
class CampusAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        if obj and (Aluno.objects.filter(campus=obj) or Professor.objects.filter(campus=obj)):
            return False
        return True

