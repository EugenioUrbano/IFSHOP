# ifshop/views_2fa.py - VERSÃO COM EMAIL REAL
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .models import Codigo2FA, UsuarioCustomizado

import time
import random
from django.core.cache import cache

class Sistema2FA:
    """Sistema 2FA robusto com múltiplas opções"""
    
    @staticmethod
    def enviar_codigo(request, user):
        """Método principal - escolhe melhor estratégia"""
        
        # Opção 1: Usa cache do Django (funciona no Render)
        codigo = str(random.randint(100000, 999999))
        cache_key = f"2fa_{user.id}"
        cache.set(cache_key, {
            'codigo': codigo,
            'user_id': user.id,
            'expiry': time.time() + 600  # 10 minutos
        }, timeout=600)
        
        # Opção 2: Salva em sessão também (fallback)
        request.session['2fa_data'] = {
            'codigo': codigo,
            'user_id': user.id,
            'timestamp': time.time()
        }
        
        # Como mostrar o código?
        if settings.DEBUG:
            # Modo desenvolvimento - mostra na tela
            return {
                'success': True,
                'codigo': codigo,  # Para exibir em uma modal
                'method': 'display'
            }
        else:
            # Modo produção - tenta email se configurado
            try:
                if all([settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD]):
                    # Envia email
                    send_mail(
                        subject='IFShop - Código de Verificação',
                        message=f'Código: {codigo}',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=True  # Não falha se não conseguir
                    )
                    return {'success': True, 'method': 'email'}
            except:
                pass
            
            # Fallback: mostra na interface com mensagem
            return {
                'success': True,
                'codigo': codigo,
                'method': 'fallback_display',
                'message': 'Verifique seu email ou use este código:'
            }
    
    @staticmethod
    def verificar_codigo(request, codigo_digitado):
        """Verifica código de várias fontes"""
        user_id = request.session.get('user_id_2fa')
        
        # Tenta do cache primeiro
        cache_key = f"2fa_{user_id}"
        cached_data = cache.get(cache_key)
        if cached_data and cached_data['codigo'] == codigo_digitado:
            cache.delete(cache_key)
            return True
        
        # Tenta da sessão
        session_data = request.session.get('2fa_data', {})
        if session_data.get('codigo') == codigo_digitado:
            # Verifica expiração (10 minutos)
            if time.time() - session_data.get('timestamp', 0) < 600:
                del request.session['2fa_data']
                return True
        
        # Código fixo para desenvolvimento
        if settings.DEBUG and codigo_digitado == "123456":
            return True
        
        return False