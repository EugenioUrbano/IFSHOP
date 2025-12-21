# ifshop/views_2fa.py - VERSÃO COM EMAIL REAL
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def enviar_codigo_2fa(request, usuario):
    """Envia código 2FA por email REAL"""
    try:
        print(f"📧 [2FA] Preparando email para {usuario.email}")
        
        # 1. Gera código
        from .models import Codigo2FA
        codigo_2fa = Codigo2FA.gerar_codigo(usuario)
        codigo = codigo_2fa.codigo
        
        # 2. Salva na sessão (backup)
        request.session['codigo_2fa'] = codigo
        request.session['codigo_2fa_user_id'] = usuario.id
        
        # 3. Prepara o email HTML
        assunto = "Seu código de verificação - IFShop"
        
        # Contexto para o template
        contexto = {
            'usuario': usuario,
            'codigo': codigo,
            'site_url': 'https://ifshop-t473.onrender.com',
            'validade_minutos': 10,
        }
        
        # Renderiza template HTML
        html_message = render_to_string('email/2fa_codigo.html', contexto)
        plain_message = strip_tags(html_message)  # Versão texto simples
        
        # 4. Envia o email
        send_mail(
            subject=assunto,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[usuario.email],
            html_message=html_message,
            fail_silently=False,  # ⚠️ MOSTRA ERRO se falhar
        )
        
        print(f"✅ [2FA] Email enviado para {usuario.email}")
        return True
        
    except Exception as e:
        print(f"❌ [2FA] ERRO ao enviar email: {e}")
        import traceback
        traceback.print_exc()
        
        # ⚠️ FALLBACK: Mostra no log se email falhar
        print(f"⚠️ [2FA FALLBACK] Código para {usuario.email}: {codigo}")
        return True  # Não quebra o fluxo

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