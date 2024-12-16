from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Camiseta, Pedido, UsuarioCustomizado

class CustomUserAdmin(UserAdmin):
    model = UsuarioCustomizado
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('vendedor',)}), 
    )
    list_display = UserAdmin.list_display + ('vendedor',)

admin.site.register(Camiseta)
admin.site.register(Pedido)
admin.site.register(UsuarioCustomizado, CustomUserAdmin)