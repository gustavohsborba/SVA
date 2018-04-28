from django.contrib import admin
from sva.models import *

# Register your models here.
admin.site.register(Curso)
admin.site.register(Aluno)
admin.site.register(Empresa)
admin.site.register(Professor)
admin.site.register(AreaAtuacao)

@admin.register(Campus)
class CampusAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        if obj and Curso.objects.filter(campus=obj):
            return False
        return True