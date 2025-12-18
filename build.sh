#!/usr/bin/env bash
# build.sh

# Instala todas as dependências
pip install -r requirements.txt

# Coleta arquivos estáticos
python manage.py collectstatic --noinput

# Aplica migrações do banco de dados
python manage.py migrate