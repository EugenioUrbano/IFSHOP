#!/usr/bin/env bash
# build.sh

# Instala dependências
pip install -r requirements.txt

# Coleta arquivos estáticos
python manage.py collectstatic --noinput

# Aplica migrações
python manage.py migrate