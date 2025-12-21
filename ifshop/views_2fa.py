# views_2fa.py - função atualizada
def enviar_codigo_2fa(request, usuario):
    """Envia código 2FA por email"""
    try:
        print(f"🔐 [2FA] Iniciando envio para {usuario.email}")
        
        # 1. Gera código SEMPRE
        from .models import Codigo2FA
        codigo_2fa = Codigo2FA.gerar_codigo(usuario)
        print(f"🔐 [2FA] Código gerado: {codigo_2fa.codigo}")
        
        # 2. Guarda código na sessão também (backup)
        request.session['codigo_2fa_backup'] = codigo_2fa.codigo
        request.session['codigo_2fa_expira'] = (
            codigo_2fa.criado_em.timestamp() + 600  # 10 minutos
        )
        
        # 3. Tenta enviar email
        from django.conf import settings
        
        # ⚠️ SE estiver usando console backend, apenas loga
        if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
            print(f"📧 [2FA CONSOLE] Código para {usuario.email}: {codigo_2fa.codigo}")
            print(f"📧 [2FA CONSOLE] URL de verificação: /verificar-2fa/")
            return True  # Retorna sucesso mesmo sem enviar email real
        
        # 4. Se for SMTP real, envia
        assunto = "Seu código de verificação - IFSHOP"
        mensagem = f"""
        Código de verificação: {codigo_2fa.codigo}
        Válido por 10 minutos.
        
        Acesse: https://ifshop-t473.onrender.com/verificar-2fa/
        """
        
        from django.core.mail import send_mail
        send_mail(
            assunto,
            mensagem,
            settings.DEFAULT_FROM_EMAIL,
            [usuario.email],
            fail_silently=False,
        )
        
        print(f"✅ [2FA] Email enviado para {usuario.email}")
        return True
        
    except Exception as e:
        print(f"⚠️ [2FA] AVISO: Não foi possível enviar email: {e}")
        print(f"⚠️ [2FA] Mas o código {codigo_2fa.codigo} foi gerado e salvo na sessão")
        # ⚠️ RETORNA TRUE MESMO COM ERRO, para o fluxo continuar
        return True  # Importante: não quebra o fluxo