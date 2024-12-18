from django.contrib.auth.backends import BaseBackend
from .models import UsuarioCustomizado

class EmailBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UsuarioCustomizado.objects.get(email=username)
            if user.check_password(password):
                return user
        except UsuarioCustomizado.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return UsuarioCustomizado.objects.get(pk=user_id)
        except UsuarioCustomizado.DoesNotExist:
            return None