import os
from pathlib import Path
from dotenv import load_dotenv
import africastalking
from datetime import timedelta

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
DEBUG = os.getenv('DEBUG') == 'True'

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'rest_framework',
    'api',
    'drf_yasg',
    'rest_framework_simplejwt',
    'mozilla_django_oidc',
    'rest_framework_simplejwt.token_blacklist'
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

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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



WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE'),
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

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

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
        #'rest_framework.permissions.AllowAny',  # Allow unauthenticated requests
    ),
}


# Africa's Talking Configuration
africastalking.initialize(
    username=os.getenv('AFRICASTALKING_USERNAME'),
    api_key=os.getenv('AFRICASTALKING_API_KEY')
)

# OIDC Configuration
OIDC_AUDIENCE = os.getenv('OIDC_AUDIENCE')
OIDC_ISSUER = os.getenv('OIDC_ISSUER')
OIDC_JWKS_URL = os.getenv('OIDC_JWKS_URL')

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication backends
AUTHENTICATION_BACKENDS = [
    'mozilla_django_oidc.auth.OIDCAuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
]


# OIDC Configuration
OIDC_RP_CLIENT_ID = os.getenv('OIDC_RP_CLIENT_ID')
OIDC_RP_CLIENT_SECRET = os.getenv('OIDC_RP_CLIENT_SECRET')
OIDC_DOMAIN= os.getenv('OIDC_DOMAIN')
OIDC_OP_AUTHORIZATION_ENDPOINT = f'https://{OIDC_DOMAIN}/authorize'
OIDC_OP_TOKEN_ENDPOINT = f'https://{OIDC_DOMAIN}/oauth/token'
OIDC_OP_USER_ENDPOINT = f'https://{OIDC_DOMAIN}/userinfo'
OIDC_OP_LOGOUT_ENDPOINT = f'https://{OIDC_DOMAIN}/v2/logout'
OIDC_OP_JWKS_ENDPOINT = f'https://{OIDC_DOMAIN}/.well-known/jwks.json'
OIDC_RP_SIGN_ALGO = 'RS256'

# OIDC callback URL
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
OIDC_AUTHENTICATION_CALLBACK_URL_NAME = 'oidc_authentication_callback'


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),  # Optional
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# Session management
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'  # Better for OIDC flow
SESSION_COOKIE_NAME = 'customers_orders_sessionid'
SESSION_COOKIE_SAMESITE = 'Lax'  # Required for cross-domain OIDC flow
CSRF_COOKIE_SAMESITE = 'Lax'
OIDC_STATE_STORE = True  # Explicitly enable state storage
OIDC_STORE_ACCESS_TOKEN = True  # Required for proper state handling
OIDC_STORE_ID_TOKEN = True  # Required for JWT validation
OIDC_RP_SCOPES = 'openid profile email'  # Required scopes