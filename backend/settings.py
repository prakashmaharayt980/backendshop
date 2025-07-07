"""
Django settings for backend project.

Enhanced for a production-like environment using SQLite.
For a higher-scale production deployment, consider switching to PostgreSQL.
"""

from pathlib import Path
import os
from datetime import timedelta
from decouple import config, Csv
import dj_database_url
import json
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY',default='django-insecure-i0&fgil%q)pv-kcffqm6$^hr*=wgra92qo40e@asw%y0=gd%sj')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)
FIREBASE_SERVICE_ACCOUNT_KEY= os.path.join(BASE_DIR,'./thelocalstorageFirebasekey.json')
# FIREBASE_SERVICE_ACCOUNT_KEY= json.loads(os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON"))
ALLOWED_HOSTS = [

   "thelocalmarket.shop",
    "admin-localmarket.vercel.app",
    "backendshop-oy2c.onrender.com",
"*"
]

ALLOWED_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS',
]

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
"https://www.thelocalmarket.shop",
"https://admin-localmarket.vercel.app",
"https://backendshop-oy2c.onrender.com",
" http://localhost:8001",
" http://localhost:8080",
'exp://vsw6if0-prakashmahara-8081.exp.direct'

]

# Application definition
INSTALLED_APPS = [
    # Required for django-allauth
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'corsheaders',
 'rest_framework.authtoken',
 'rest_framework_simplejwt.token_blacklist', 
   'notification',
    'inventory',
    'user',
    # 'storages'
]

# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='thelocalmarketshop')
# AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='e898ab54edbeb40aa33dd855c228e398')
# AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='707878b2d602354b84ec57da28a120bb68eb8caeb35b31a3c7af31091051f1fa')
# AWS_S3_ENDPOINT_URL = config('AWS_S3_ENDPOINT_URL', default='https://043d6fcd7a801354563bfe9ec6c6f1f6.r2.cloudflarestorage.com')
# AWS_S3_SIGNATURE_VERSION = config('AWS_S3_SIGNATURE_VERSION', default='s3v4')
# AWS_S3_ADDRESSING_STYLE = config('AWS_S3_ADDRESSING_STYLE', default='virtual')
# AWS_DEFAULT_ACL = None
# AWS_QUERYSTRING_AUTH = False


MIDDLEWARE = [ 
    'corsheaders.middleware.CorsMiddleware',

    'django.middleware.security.SecurityMiddleware',


    'django.contrib.sessions.middleware.SessionMiddleware',
    
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # Specify your template directories here if any
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # Required by allauth
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'


STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# DATABASES = {
#     'default': dj_database_url.parse('postgresql://thelocalmarketusername:OEqn5zbbenqj1hAaB1zuanLxYPAtIeti@dpg-d0nan7emcj7s73dphfd0-a.singapore-postgres.render.com/thelocalmarketdbname')
# }

# DATABASES = {
#     'default': dj_database_url.parse('postgresql://thelocalmarketusername:OEqn5zbbenqj1hAaB1zuanLxYPAtIeti@dpg-d0nan7emcj7s73dphfd0-a/thelocalmarketdbname')
# }



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Password validation
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

# Internationalization settings
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.{AWS_S3_ENDPOINT_URL.replace('https://', '')}/"
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Use WhiteNoise to compress and serve static files


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST framework configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}

# SimpleJWT configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
}

# Custom User Model
AUTH_USER_MODEL = 'user.CustomUser'

# Email settings for sending emails
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

# Django Sites and allauth settings
SITE_ID = 1

ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']
ACCOUNT_USER_MODEL_USERNAME_FIELD = None

REST_USE_JWT = True

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': config('GOOGLE_CLIENT_ID'),
            'secret': config('GOOGLE_CLIENT_SECRET'),
            'key': ''
        },
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    }
}


LOGGING = {
  'version': 1,
  'disable_existing_loggers': False,
  'handlers': { 'console': { 'class': 'logging.StreamHandler' } },
  'root': { 'handlers': ['console'], 'level': 'DEBUG' },
}
  