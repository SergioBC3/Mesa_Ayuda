

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

from dotenv import load_dotenv
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.environ.get('SECRET_KEY', 'clave-de-desarrollo-no-usar-en-produccion')

DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = [o for o in os.environ.get('CSRF_TRUSTED_ORIGINS', 'https://*.onrender.com').split(',') if o]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tecnicos',
    'tickets',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
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
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage'},
}



MICROSERVICIO_URL = os.environ.get('MICROSERVICIO_URL', 'https://mesa-ayuda-nnue.onrender.com')
URL_LECTURA_PRINCIPAL = os.environ.get('URL_LECTURA_PRINCIPAL', MICROSERVICIO_URL)
URL_LECTURA_RESPALDO = os.environ.get('URL_LECTURA_RESPALDO', '')
URL_INSERTAR = os.environ.get('URL_INSERTAR', '')      
URL_ACTUALIZAR = os.environ.get('URL_ACTUALIZAR', '')  
URL_ELIMINAR = os.environ.get('URL_ELIMINAR', '')     


TIMEOUT_PRINCIPAL = float(os.environ.get('TIMEOUT_PRINCIPAL', '8'))
TIMEOUT_RESPALDO = float(os.environ.get('TIMEOUT_RESPALDO', '60'))
TIMEOUT_ESCRITURA = float(os.environ.get('TIMEOUT_ESCRITURA', '60'))
CB_UMBRAL_FALLOS = int(os.environ.get('CB_UMBRAL_FALLOS', '2'))
CB_SEGUNDOS_ABIERTO = float(os.environ.get('CB_SEGUNDOS_ABIERTO', '30'))

GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
