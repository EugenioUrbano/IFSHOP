# ifshop/views_2fa.py - VERSÃO COMPLETA E FUNCIONAL
import random
import time
from django.conf import settings
from django.contrib import messages

def gerar_codigo_aleatorio():
    """Gera um código numérico de 6 dígitos aleatório"""
    return str(random.randint(100000, 999999))

def enviar_codigo_2fa(request, user):
    """
    Sistema 2FA simplificado - gera código aleatório e salva na sessão
    """
    try:
        # Gera código aleatório de 6 dígitos
        codigo = gerar_codigo_aleatorio()
        
        # Salva na sessão do Django com timestamp
        request.session['codigo_2fa'] = codigo
        request.session['user_id_2fa'] = user.id
        request.session['2fa_expiry'] = time.time() + 600  # 10 minutos
        request.session['2fa_tentativas'] = 0  # Contador de tentativas
        
        # Mostra o código no CONSOLE (log) - como você pediu
        print(f"🔐 [2FA] Código gerado para {user.email}: {codigo}")
        print(f"🔐 [2FA] Válido por 10 minutos")
        
        # Se estiver em modo DEBUG, mostra na interface também
        if settings.DEBUG:
            messages.info(request, f'🔐 Código 2FA (para testes): {codigo}')
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao gerar código 2FA: {e}")
        # Fallback: código fixo
        request.session['codigo_2fa'] = "123456"
        request.session['user_id_2fa'] = user.id
        return True

def verificar_codigo_2fa(request, codigo_digitado):
    """
    Verifica se o código digitado está correto
    """
    # Pega dados da sessão
    codigo_correto = request.session.get('codigo_2fa')
    user_id = request.session.get('user_id_2fa')
    expiry = request.session.get('2fa_expiry', 0)
    
    # Verifica se a sessão tem dados
    if not all([codigo_correto, user_id]):
        print("❌ [2FA] Dados de verificação não encontrados na sessão")
        return False
    
    # Verifica expiração (10 minutos)
    if time.time() > expiry:
        print("❌ [2FA] Código expirado")
        messages.error(request, 'Código expirado. Faça login novamente.')
        return False
    
    # Incrementa tentativas
    tentativas = request.session.get('2fa_tentativas', 0) + 1
    request.session['2fa_tentativas'] = tentativas
    
    # Limite de tentativas (3)
    if tentativas > 3:
        print(f"❌ [2FA] Muitas tentativas para usuário {user_id}")
        messages.error(request, 'Muitas tentativas. Faça login novamente.')
        # Limpa sessão 2FA
        limpar_sessao_2fa(request)
        return False
    
    # Compara códigos
    if codigo_digitado == codigo_correto:
        print(f"✅ [2FA] Código válido para usuário {user_id}")
        
        # Limpa dados 2FA da sessão após verificação bem-sucedida
        limpar_sessao_2fa(request)
        
        return True
    else:
        print(f"❌ [2FA] Código inválido. Tentativa {tentativas}/3")
        print(f"❌ [2FA] Digitado: {codigo_digitado}, Esperado: {codigo_correto}")
        return False

def limpar_sessao_2fa(request):
    """Limpa dados 2FA da sessão"""
    keys_to_remove = ['codigo_2fa', 'user_id_2fa', '2fa_expiry', '2fa_tentativas']
    for key in keys_to_remove:
        if key in request.session:
            del request.session[key]