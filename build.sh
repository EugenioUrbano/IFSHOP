echo "=== 1. Instalando dependências ==="
pip install --upgrade pip
pip install -r requirements.txt

echo "=== 2. Verificando Cloudinary ==="
python -c "
try:
    import cloudinary
    print('✅ Cloudinary instalado')
except ImportError:
    print('❌ Cloudinary NÃO instalado')
    exit 1
"

echo "=== 3. Aplicando migrações ==="
python manage.py migrate

echo "=== 4. Criando superusuário (se necessário) ==="
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@ifshop.com', 'admin123')
    print('✅ Superusuário criado')
"

echo "=== 5. Coletando arquivos estáticos ==="
python manage.py collectstatic --noinput --clear

echo "=== 6. Verificando configurações ==="
python manage.py check --deploy

echo "=== ✅ Build completo! ==="