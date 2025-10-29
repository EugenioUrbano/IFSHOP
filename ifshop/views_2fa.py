from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.core.mail import send_mail
from django.conf import settings
from .models import Codigo2FA, UsuarioCustomizado

def enviar_codigo_2fa(request, usuario):
    """Envia código 2FA por email"""
    codigo_2fa = Codigo2FA.gerar_codigo(usuario)
    
    assunto = "Seu código de verificação - IFSHOP"
    mensagem = f"""
    Olá {usuario.nome},
    
    Seu código de verificação em duas etapas é: {codigo_2fa.codigo}
    
    Este código expira em 10 minutos.
    
    Se você não solicitou este código, ignore este email.
    
    Atenciosamente,
    Equipe IFSHOP
    """
    
    send_mail(
        assunto,
        mensagem,
        settings.DEFAULT_FROM_EMAIL,
        [usuario.email],
        fail_silently=False,
    )
    
    return codigo_2fa.codigo

def verificar_2fa(request):
    """Página para verificar código 2FA"""
    if not request.session.get('usuario_2fa_id'):
        return redirect('login')
    
    if request.method == 'POST':
        codigo_digitado = request.POST.get('codigo')
        usuario_id = request.session.get('usuario_2fa_id')
        
        try:
            usuario = UsuarioCustomizado.objects.get(id=usuario_id)
            codigo_2fa = Codigo2FA.objects.filter(
                usuario=usuario, 
                codigo=codigo_digitado
            ).first()
            
            if codigo_2fa and codigo_2fa.esta_valido():
                # Código válido - faz login
                codigo_2fa.utilizado = True
                codigo_2fa.save()
                
                from ifshop.backends import EmailBackend
                login(request, usuario, backend='ifshop.backends.EmailBackend')
                
                # Limpa sessão
                request.session.pop('usuario_2fa_id', None)
                
                return redirect('/')
            else:
                return render(request, '2fa/verificar.html', {
                    'error': 'Código inválido ou expirado'
                })
                
        except UsuarioCustomizado.DoesNotExist:
            return redirect('login')
    
    return render(request, '2fa/verificar.html')

def reenviar_codigo_2fa(request):
    """Reenvia código 2FA"""
    if not request.session.get('usuario_2fa_id'):
        return redirect('login')
    
    usuario_id = request.session.get('usuario_2fa_id')
    usuario = UsuarioCustomizado.objects.get(id=usuario_id)
    
    enviar_codigo_2fa(request, usuario)
    
    return render(request, '2fa/verificar.html', {
        'success': 'Novo código enviado para seu email!'
    })