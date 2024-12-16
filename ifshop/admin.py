from django.contrib import admin

from .models import Camiseta, Pedido, UsuarioCustomizado

admin.site.register(Camiseta)
admin.site.register(Pedido)
admin.site.register(UsuarioCustomizado)