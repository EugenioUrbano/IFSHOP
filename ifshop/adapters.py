from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from django.db import IntegrityError

UsuarioCustomizado = get_user_model()

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        
        # Para Google
        if sociallogin.account.provider == 'google':
            extra_data = sociallogin.account.extra_data
            user.nome = extra_data.get('name', '')
            # O email já é preenchido automaticamente pelo allauth
        
        return user
    
    def save_user(self, request, sociallogin, form=None):
        """
        Garante que o usuário seja salvo corretamente com os campos customizados
        """
        user = super().save_user(request, sociallogin, form=form)
        
        # Se o usuário não tem nome, tenta obter do Google
        if not user.nome and sociallogin.account.provider == 'google':
            extra_data = sociallogin.account.extra_data
            user.nome = extra_data.get('name', '')
        
        # Se ainda não tem nome, usa first_name + last_name
        if not user.nome:
            first_name = getattr(user, 'first_name', '')
            last_name = getattr(user, 'last_name', '')
            user.nome = f"{first_name} {last_name}".strip() or user.email.split('@')[0]
            
        # Garante que tem username
        if not user.username:
            base_username = user.email.split('@')[0]
            username = base_username
            counter = 1
            
            while UsuarioCustomizado.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
                
            user.username = username
        
        try:
            user.save()
        except IntegrityError as e:
            # Se houver erro de integridade (username duplicado), tenta novamente
            if 'username' in str(e):
                base_username = user.email.split('@')[0]
                username = f"{base_username}_{user.pk}"  # Usa PK para garantir unicidade
                user.username = username
                user.save()
        
        return user
    
    def pre_social_login(self, request, sociallogin):
        """
        Executado antes do login social - útil para debug
        """
        print(f"🔧 Pré-login social: {sociallogin.account.provider}")
        print(f"📧 Email: {sociallogin.user.email}")
        print(f"👤 Nome: {getattr(sociallogin.user, 'nome', 'Não definido')}")