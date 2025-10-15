import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Development settings
DEBUG = True

# Secret key (use env var in prod)
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'dev-secret-key-change-me-please-1234567890')

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
]

INSTALLED_APPS = [
    # 'jazzmin',  # Comentado temporalmente
    'appsistem.apps.AppsistemConfig',
    'panel',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'import_export',
    'django_recaptcha',
]

# Required middleware for sessions, auth, and messages
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Agregar middleware personalizado para desarrollo
if DEBUG:
    MIDDLEWARE.append('appsistem.middleware.RecaptchaDevMiddleware')

ROOT_URLCONF = 'sistema.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'panel.context_processors.notifications',  # <- añade unread_count
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sistema.wsgi.application'

# SQLite database (default)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Internationalization
LANGUAGE_CODE = 'es-VE'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static and media
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'appsistem/static')]
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email (Gmail con App Password)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

EMAIL_HOST_USER = 'moisestodoroki@gmail.com'
EMAIL_HOST_PASSWORD = 'wavkbgzxflznsjdq'   # sin espacios
DEFAULT_FROM_EMAIL = 'Sistema UCS <moisestodoroki@gmail.com>'
EMAIL_TIMEOUT = 20

# reCAPTCHA Configuration
import os

# Configuración por defecto (será sobrescrita en DEBUG)
RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY', '6Lfxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')  # Reemplazar con tu clave real
RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY', '6Lfxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')  # Reemplazar con tu clave real

# En desarrollo, ignorar variables de entorno y usar configuración local
if DEBUG:
    # Forzar configuración local (ignorar variables de entorno)
    RECAPTCHA_PUBLIC_KEY = '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'
    RECAPTCHA_PRIVATE_KEY = '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'

# Configuración de reCAPTCHA
RECAPTCHA_DOMAIN = 'www.google.com'
RECAPTCHA_DEFAULT_ACTION = 'generic'
RECAPTCHA_SCORE_THRESHOLD = 0.5
RECAPTCHA_VERIFY_REQUEST_TIMEOUT = 10

# Configuración robusta para desarrollo local
if DEBUG:
    # Configuración específica para desarrollo local
    RECAPTCHA_TESTING = True
    RECAPTCHA_DOMAIN = 'www.google.com'
    RECAPTCHA_VERIFY_REQUEST_TIMEOUT = 10
    
    # Configuración adicional para evitar mensajes de prueba
    RECAPTCHA_DISABLE = False
    RECAPTCHA_USE_SSL = True
    
    print("MODO DESARROLLO: reCAPTCHA configurado para localhost")
    print(f"   Clave Publica: {RECAPTCHA_PUBLIC_KEY}")
    print(f"   Testing Mode: {RECAPTCHA_TESTING}")

# Silenciar TODAS las advertencias de reCAPTCHA
SILENCED_SYSTEM_CHECKS = [
    'captcha.recaptcha_test_key_error',
    'django_recaptcha.recaptcha_test_key_error',
    'captcha.recaptcha_test_key_warning',
    'django_recaptcha.recaptcha_test_key_warning'
]
