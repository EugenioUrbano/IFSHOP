from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import ProdutoBase, Camiseta, PedidoBase, PedidoCamiseta, UsuarioCustomizado, Curso, Avaliacao


admin.site.register(Camiseta)
admin.site.register(ProdutoBase)
admin.site.register(PedidoBase)
admin.site.register(PedidoCamiseta)
admin.site.register(UsuarioCustomizado)

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ['nome']
    
@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ['produto', 'cliente', 'estrelas', 'data_criacao', 'tem_comentario']
    list_filter = ['estrelas', 'data_criacao', 'produto']
    search_fields = ['produto__titulo', 'cliente__nome', 'comentario']
    readonly_fields = ['data_criacao', 'atualizado_em']
    
    def tem_comentario(self, obj):
        return bool(obj.comentario)
    tem_comentario.boolean = True
    tem_comentario.short_description = 'Tem Comentário'