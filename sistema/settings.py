import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Development settings
DEBUG = True

# Secret key (use env var in prod)
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'dev-secret-key-change-me-please-1234567890')

<<<<<<< HEAD
ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
]
=======
ALLOWED_HOSTS ['sistemaucsproyecto.pythonanywhere.com', '127.0.0.1']

>>>>>>> cad832e520c2d7abef0436fc1fce62aa652d15c4
INSTALLED_APPS = [
    'jazzmin',
    'appsistem.apps.AppsistemConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
INSTALLED_APPS = [
    'jazzmin',
    'appsistem.apps.AppsistemConfig',
    'panel',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'captcha',
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
<<<<<<< HEAD
EMAIL_TIMEOUT = 20
=======
EMAIL_TIMEOUT = 20
>>>>>>> cad832e520c2d7abef0436fc1fce62aa652d15c4
