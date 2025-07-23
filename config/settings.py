from  decouple import config
import os
from pathlib import Path
from django.contrib.messages import constants as messages

EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-qbv1*5j=rxzji_@%1ma_3d9&$fz$o315!xwv0g#x*9dob&nmgj'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False


ALLOWED_HOSTS = ['ifshopweb.northeurope.cloudapp.azure.com', '52.158.32.93', '127.0.0.1', 'localhost']

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# Application definition

INSTALLED_APPS = [
    'ifshop',
    "crispy_forms",
    "crispy_bootstrap5",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

CRISPY_TEMPLATE_PACK = "bootstrap5"

# CONFIGURAÇÃOM LOGIN

AUTH_USER_MODEL = 'ifshop.UsuarioCustomizado'

LOGIN_URL = '/login/'

LOGIN_REDIRECT_URL = '/perfil/'

LOGOUT_REDIRECT_URL = '/login/'

AUTHENTICATION_BACKENDS = ['ifshop.backends.EmailBackend']

# CONFIGURAÇÃOM LOGIN

# CONFIGURAÇÃO RESTAURAÇÃO DE SENHA PELO CONSOLE
 
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"  # Servidor SMTP do Gmail (ou de outro provedor)
EMAIL_PORT = 587  # Porta do Gmail (TLS)
EMAIL_USE_TLS = True  # Segurança
EMAIL_USE_SSL = False  # Não usar SSL (TLS já é suficiente)
EMAIL_HOST_USER = config("EMAIL_HOST_USER")  # Carregar do .env
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")  # Carregar do .env
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# CONFIGURAÇÃO RESTAURAÇÃO DE SENHA PELO CONSOLE

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'ifshop.context_processors.pedidos_usuario',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  
        'NAME': config('NAME_BD'),              
        'USER': config('USER_BD'),                 
        'PASSWORD': config('PASSWORD_BD'),               
        'HOST': 'localhost',                   
        'PORT': '3306',    
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Recife'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

MEDIA_URL = '/media/'
MEDIA_ROOT = '/var/www/html/IFSHOP-PROJETO_FINAL/media/'

STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/html/IFSHOP-PROJETO_FINAL/static/'



# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


