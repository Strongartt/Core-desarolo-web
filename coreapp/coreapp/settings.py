# coreapp/settings.py

from pathlib import Path
import dj_database_url

# Si usas python-dotenv, descomenta estas dos líneas:
# from dotenv import load_dotenv
# load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure--xuu@yrcudj$@$_gpm&jx@!*oe&s!p$nfm0e$bbm)4guoq8s7*'
DEBUG = True
ALLOWED_HOSTS = ["https://core-desarolo-web.onrender.com"]

# Aplicaciones instaladas
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'gestion',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'coreapp.urls'

# Plantillas (templates)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Directorio de plantillas de nivel proyecto
        'DIRS': [ BASE_DIR / 'templates' ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',  
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'coreapp.wsgi.application'

# Base de datos (PostgreSQL en Render)
DATABASES = {
    'default': dj_database_url.parse(
        'postgresql://postgresql_django_syv1_user:fkxXPwAwvYk8rYwCwy1HA7p3NQn07YW0@'
        'dpg-d0d6gpadbo4c73duc1tg-a.oregon-postgres.render.com/'
        'postgresql_django_syv1',
        conn_max_age=600,
        ssl_require=True
    )
}

# Validadores de contraseña
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internacionalización
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Archivos estáticos
STATIC_URL = 'static/'

# PK por defecto
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/accounts/login/'           # dónde envía si no estás logueado
LOGIN_REDIRECT_URL = '/usuarios/'        # tras hacer login
LOGOUT_REDIRECT_URL = '/accounts/login/' # tras hacer logout


