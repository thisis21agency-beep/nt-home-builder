import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'dev-only-change-me')
DEBUG = os.getenv('DJANGO_DEBUG', '0') == '1'
ALLOWED_HOSTS = [x.strip() for x in os.getenv('DJANGO_ALLOWED_HOSTS','localhost,127.0.0.1,.vercel.app').split(',') if x.strip()]
CSRF_TRUSTED_ORIGINS = [x.strip() for x in os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS','https://*.vercel.app').split(',') if x.strip()]
RNT_STOREFRONT_ORIGIN = os.getenv('RNT_STOREFRONT_ORIGIN','https://www.ruffntumblekids.com').rstrip('/')
PUBLIC_MEDIA_BASE_URL = os.getenv('PUBLIC_MEDIA_BASE_URL','').rstrip('/')

INSTALLED_APPS = [
    'django.contrib.admin','django.contrib.auth','django.contrib.contenttypes',
    'django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles',
    'homepage',
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
ROOT_URLCONF='config.urls'
TEMPLATES=[{
    'BACKEND':'django.template.backends.django.DjangoTemplates',
    'DIRS':[],
    'APP_DIRS':True,
    'OPTIONS':{'context_processors':[
        'django.template.context_processors.request','django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]
WSGI_APPLICATION='config.wsgi.application'
ASGI_APPLICATION='config.asgi.application'

database_url = os.getenv('DATABASE_URL', '').strip()
if database_url:
    DATABASES = {
        'default': dj_database_url.parse(database_url, conn_max_age=0, conn_health_checks=True)
    }
elif os.getenv('DB_NAME'):
    DATABASES={'default':{
        'ENGINE':'django.db.backends.postgresql','NAME':os.getenv('DB_NAME'),
        'USER':os.getenv('DB_USER'),'PASSWORD':os.getenv('DB_PASSWORD'),
        'HOST':os.getenv('DB_HOST','localhost'),'PORT':os.getenv('DB_PORT','5432'),
        'CONN_MAX_AGE':0,
    }}
else:
    DATABASES={'default':{'ENGINE':'django.db.backends.sqlite3','NAME':BASE_DIR/'db.sqlite3'}}

AUTH_PASSWORD_VALIDATORS=[
    {'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
LANGUAGE_CODE='en-gb'
TIME_ZONE='Africa/Lagos'
USE_I18N=True
USE_TZ=True
STATIC_URL='/static/'
STATIC_ROOT=BASE_DIR/'staticfiles'
MEDIA_URL='/media/'
MEDIA_ROOT=BASE_DIR/'media'
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
LOGIN_URL='/admin/login/'
LOGIN_REDIRECT_URL='/builder/home/'
SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO','https')
SESSION_COOKIE_SECURE=not DEBUG
CSRF_COOKIE_SECURE=not DEBUG
X_FRAME_OPTIONS='SAMEORIGIN'

# Optional S3-compatible DigitalOcean Spaces storage for uploaded homepage media.
if os.getenv('SPACES_ACCESS_KEY') and os.getenv('SPACES_SECRET_KEY') and os.getenv('SPACES_BUCKET_NAME'):
    AWS_ACCESS_KEY_ID=os.getenv('SPACES_ACCESS_KEY')
    AWS_SECRET_ACCESS_KEY=os.getenv('SPACES_SECRET_KEY')
    AWS_STORAGE_BUCKET_NAME=os.getenv('SPACES_BUCKET_NAME')
    AWS_S3_ENDPOINT_URL=os.getenv('SPACES_ENDPOINT_URL','https://lon1.digitaloceanspaces.com')
    AWS_S3_REGION_NAME=os.getenv('SPACES_REGION','lon1')
    AWS_S3_ADDRESSING_STYLE='path'
    AWS_QUERYSTRING_AUTH=False
    AWS_DEFAULT_ACL='public-read' if os.getenv('SPACES_PUBLIC','0')=='1' else None
    STORAGES={
        'default':{'BACKEND':'storages.backends.s3.S3Storage'},
        'staticfiles':{'BACKEND':'django.contrib.staticfiles.storage.StaticFilesStorage'},
    }
