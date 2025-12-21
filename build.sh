echo "=== 1. Instalando dependências ==="
pip install --upgrade pip
pip install -r requirements.txt

set -o errexit

echo "=== 1. Instalando dependências ==="
pip install --upgrade pip
pip install -r requirements.txt

echo "=== 2. Configurando Cloudinary ==="
# Verifica se as variáveis do Cloudinary existem
if [ -n "$CLOUDINARY_CLOUD_NAME" ]; then
    echo "✅ Cloudinary configurado"
else
    echo "⚠️  Cloudinary não configurado - imagens podem não funcionar"
fi

echo "=== 3. Aplicando migrações ==="
python manage.py migrate

echo "=== 4. Coletando arquivos estáticos ==="
python manage.py collectstatic --noinput

echo "=== ✅ Build completo! ==="