import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv(
    'SECRET_KEY',
    'django-insecure-&j0*)pmo7$a_+8vh5%s^h8mq8mc2!%=a1s34=^7$gbs%=z=2f('
)

DEBUG = True

ALLOWED_HOSTS = []


INSTALLED_APPS = [
    'recipes.apps.RecipesConfig',
    'users.apps.UsersConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'djoser',
    'django_filters'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'django.middleware.locale.LocaleMiddleware',
]

ROOT_URLCONF = 'foodgram_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'foodgram_backend.wsgi.application'

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.getenv('POSTGRES_DB', 'foodgram'),
#         'USER': os.getenv('POSTGRES_USER', 'foodgram_user'),
#         'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'foodgram_password'),
#         'HOST': os.getenv('DB_HOST', 'localhost'),
#         'PORT': os.getenv('DB_PORT', 5432)
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
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

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/


# LANGUAGES = [
#     ('en-us', _('English')),
#     ('ru', _('Russian')),
# ]

# LOCALE_PATHS = [
#     os.path.join(BASE_DIR, 'recipes/translations')
# ]


LANGUAGE_CODE = 'ru'
# LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],

    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 6,
}

AUTH_USER_MODEL = 'users.User'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'collected_static'


NAME_MAX_LENGTH = 200
SLUG_MAX_LENGHT = 50

USERNAME_MAX_LENTH = 140
EMAIL_MAX_LENGTH = 256
DISPLAY_TEXT_MAX_LENGTH = 50

MAX_PORTIONS = 20
MAX_INGREDIENTS_AMOUNT = 2000
MAX_COOKING_TIME = 3 * 24 * 60

PASSWORD_MAX_LENGTH = 50
