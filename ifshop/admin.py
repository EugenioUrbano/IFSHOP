from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import ProdutoBase, Camiseta, PedidoBase, PedidoCamiseta, UsuarioCustomizado, Curso


admin.site.register(Camiseta)
admin.site.register(ProdutoBase)
admin.site.register(PedidoBase)
admin.site.register(PedidoCamiseta)
admin.site.register(UsuarioCustomizado)

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ['nome']