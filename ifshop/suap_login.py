from django.shortcuts import redirect, render
from django.contrib.auth import login
from django.conf import settings
import requests
import urllib.parse
from decouple import config
from .models import UsuarioCustomizado

def suap_login(request):
    """Redireciona para o SUAP para autorização"""
    SUAP_CLIENT_ID = config('SUAP_CLIENT_ID')
    redirect_uri = 'https://ifshop-t473.onrender.com/suap/callback/'
    
    params = {
        'client_id': SUAP_CLIENT_ID,
        'response_type': 'code',
        'scope': 'identificacao',  # ⬅️ APENAS identificação
        'redirect_uri': redirect_uri,
    }
    
    url = f"https://suap.ifrn.edu.br/o/authorize/?{urllib.parse.urlencode(params)}"
    print(f"🔗 Redirecionando para: {url}")
    return redirect(url)

def suap_callback(request):
    """Processa o retorno do SUAP e loga o usuário"""
    print("🔄 Callback do SUAP chamado!")
    print(f"📋 Parâmetros recebidos: {dict(request.GET)}")
    
    code = request.GET.get('code')
    error = request.GET.get('error')
    
    if error:
        print(f"❌ Erro do SUAP: {error}")
        return render(request, 'error.html', {'error': f'Erro do SUAP: {error}'})
    
    if not code:
        print("❌ Código não recebido")
        return render(request, 'error.html', {'error': 'Código de autorização não recebido.'})
    
    print(f"✅ Código recebido: {code}")
    
    SUAP_CLIENT_ID = config('SUAP_CLIENT_ID')
    SUAP_CLIENT_SECRET = config('SUAP_CLIENT_SECRET')
    redirect_uri = 'https://ifshop-t473.onrender.com/suap/callback/'
    
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': SUAP_CLIENT_ID,
        'client_secret': SUAP_CLIENT_SECRET,
        'redirect_uri': redirect_uri,
    }
    
    try:
        print("📞 Obtendo access token...")
        
        # Obtém access token
        token_response = requests.post(
            'https://suap.ifrn.edu.br/o/token/',
            data=token_data
        )
        
        print(f"📊 Status token: {token_response.status_code}")
        print(f"📊 Resposta token: {token_response.text}")
        
        token_response.raise_for_status()
        token_json = token_response.json()
        access_token = token_json['access_token']
        
        print(f"✅ Access token obtido: {access_token[:20]}...")
        
        # Obtém dados do usuário
        headers = {'Authorization': f'Bearer {access_token}'}
        profile_response = requests.get(
            'https://suap.ifrn.edu.br/api/eu/',
            headers=headers
        )
        
        print(f"📊 Status perfil: {profile_response.status_code}")
        
        profile_response.raise_for_status()
        user_data = profile_response.json()
        
        print(f"✅ Dados do usuário: {user_data}")
        
        # Cria ou obtém o usuário
        user = get_or_create_suap_user(user_data)
        
        # ⬇️ CORREÇÃO: Especifica o backend no login ⬇️
        from ifshop.backends import EmailBackend
        login(request, user, backend='ifshop.backends.EmailBackend')
        
        print(f"🎉 Usuário {user.email} logado com sucesso!")
        
        return redirect('/')
        
    except Exception as e:
        print(f"❌ Erro no callback: {e}")
        return render(request, 'error.html', {'error': str(e)})

def get_or_create_suap_user(user_data):
    """Cria ou obtém usuário baseado nos dados do SUAP"""
    identificacao = user_data.get('identificacao')  # Matrícula (username)
    nome_registro = user_data.get('nome_registro', '')  # Nome completo
    email = user_data.get('email', '')  # Email
    
    print(f"👤 Processando usuário: {identificacao} - {nome_registro}")
    
    # Se não veio email, cria um email baseado na matrícula
    if not email and identificacao:
        email = f"{identificacao}@aluno.ifrn.edu.br"
    
    try:
        user = UsuarioCustomizado.objects.get(email=email)
        print(f"✅ Usuário existente: {user.email}")
    except UsuarioCustomizado.DoesNotExist:
        print("📝 Criando novo usuário...")
        user = UsuarioCustomizado(
            email=email,
            username=identificacao,
            nome=nome_registro,
            is_active=True,
            telefone=None,
            curso=None,
            vendedor=False
        )
        user.set_unusable_password()
        user.save()
        print(f"✅ Novo usuário criado: {user.email}")
    
    return user