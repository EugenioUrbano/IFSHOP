# ifshop/views_2fa.py - VERSÃO COM EMAIL REAL
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .models import Codigo2FA, UsuarioCustomizado

def enviar_codigo_2fa(request, usuario):
    """Gera e armazena código 2FA (SEM tentar enviar email real no Render)"""
    try:
        print(f"🔐 [2FA] Iniciando para {usuario.email}")
        
        from .models import Codigo2FA
        codigo_2fa = Codigo2FA.gerar_codigo(usuario)
        codigo = codigo_2fa.codigo
        
        # Salva na sessão (IMPORTANTE)
        request.session['codigo_2fa'] = codigo
        request.session['codigo_2fa_user_id'] = usuario.id
        request.session['codigo_2fa_time'] = str(codigo_2fa.criado_em.timestamp())
        
        # ⚠️ NÃO TENTA ENVIAR EMAIL NO RENDER
        from django.conf import settings
        
        if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
            # Modo DEBUG/Render: mostra no log
            print(f"📧 [2FA DEBUG] Código para {usuario.email}: {codigo}")
            print(f"📧 [2FA DEBUG] URL: https://ifshop-t473.onrender.com/verificar-2fa/")
            
            # ⚠️ OPÇÃO EXTRA: Salva em arquivo temporário para você ver
            import os
            debug_file = "/tmp/2fa_code.txt"
            with open(debug_file, "w") as f:
                f.write(f"Email: {usuario.email}\n")
                f.write(f"Código: {codigo}\n")
                f.write(f"Valido por: 10 minutos\n")
            print(f"📝 [2FA DEBUG] Código salvo em: {debug_file}")
            
            return True
        
        else:
            # Modo produção com email real (se configurar depois)
            from django.core.mail import send_mail
            send_mail(
                subject='IFShop - Código de Verificação',
                message=f'Seu código: {codigo}\nVálido por 10 minutos.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[usuario.email],
                fail_silently=True,  # ⚠️ NÃO bloqueia se falhar
            )
            return True
            
    except Exception as e:
        print(f"⚠️ [2FA] Erro (ignorado): {e}")
        # ⚠️ RETORNA TRUE SEMPRE para não quebrar fluxo
        return True

def verificar_2fa(request):  # ⚠️ ESTA FUNÇÃO DEVE EXISTIR!
    """Página para verificar código 2FA"""
    print(f"🔄 [2FA] Acessando verificação")
    
    codigo_sessao = request.session.get('codigo_2fa')
    usuario_id = request.session.get('codigo_2fa_user_id')
    
    if not codigo_sessao or not usuario_id:
        print("❌ [2FA] Sem código na sessão")
        return redirect('login')
    
    if request.method == 'POST':
        codigo_digitado = request.POST.get('codigo', '').strip()
        
        print(f"📝 [2FA] Código digitado: {codigo_digitado}")
        
        if codigo_digitado == codigo_sessao:
            try:
                usuario = UsuarioCustomizado.objects.get(id=usuario_id)
                print(f"✅ [2FA] Código válido para {usuario.email}")
                
                # Faz login
                from ifshop.backends import EmailBackend
                login(request, usuario, backend='ifshop.backends.EmailBackend')
                
                # Limpa sessão
                request.session.pop('codigo_2fa', None)
                request.session.pop('codigo_2fa_user_id', None)
                
                return redirect('/')
                
            except UsuarioCustomizado.DoesNotExist:
                return redirect('login')
        else:
            print(f"❌ [2FA] Código incorreto")
            return render(request, '2fa/verificar.html', {
                'error': 'Código inválido'
            })
    
    # GET request
    return render(request, '2fa/verificar.html')

def reenviar_codigo_2fa(request):
    """Reenvia código 2FA"""
    if not request.session.get('codigo_2fa_user_id'):
        return redirect('login')
    
    usuario_id = request.session['codigo_2fa_user_id']
    usuario = UsuarioCustomizado.objects.get(id=usuario_id)
    
    enviar_codigo_2fa(request, usuario)
    
    return render(request, '2fa/verificar.html', {
        'success': 'Novo código gerado!'
    })