from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.conf import settings
from .models import Codigo2FA, UsuarioCustomizado

def enviar_codigo_2fa(request, usuario):
    """Gera código 2FA e armazena na sessão"""
    try:
        print(f"🔐 [2FA] Gerando código para {usuario.email}")
        
        # Gera código
        codigo_2fa = Codigo2FA.gerar_codigo(usuario)
        codigo = codigo_2fa.codigo
        
        print(f"🔐 [2FA] Código gerado: {codigo}")
        
        # Armazena na sessão
        request.session['codigo_2fa'] = codigo
        request.session['codigo_2fa_user_id'] = usuario.id
        
        print(f"📧 [2FA DEBUG] Código para {usuario.email}: {codigo}")
        return True
        
    except Exception as e:
        print(f"⚠️ [2FA] Erro: {e}")
        return True  # Não quebra fluxo

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