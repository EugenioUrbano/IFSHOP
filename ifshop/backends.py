from django.contrib.auth.backends import BaseBackend
from .models import UsuarioCustomizado

class EmailBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UsuarioCustomizado.objects.get(email=username)
            if user.check_password(password):
                # ⬇️ VERIFICAÇÃO 2FA - Redireciona para 2FA em vez de logar direto ⬇️
                if request and hasattr(request, 'session'):
                    from .views_2fa import enviar_codigo_2fa
                    enviar_codigo_2fa(request, user)
                    request.session['usuario_2fa_id'] = user.id
                    request.session['usuario_autenticado'] = True
                    return None  # Não loga ainda - vai para 2FA
                return user
        except UsuarioCustomizado.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return UsuarioCustomizado.objects.get(pk=user_id)
        except UsuarioCustomizado.DoesNotExist:
            return None