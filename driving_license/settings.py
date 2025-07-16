from pathlib import Path
import os
import firebase_admin
from firebase_admin import credentials
from dotenv import load_dotenv
load_dotenv()
from celery import Celery
from celery.schedules import crontab
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-%dk)v&729i3@4j9boipxr%u)l4-z6zz$dq+s-1u*&vq*h-)rdw'

DEBUG = True



# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

ALLOWED_HOSTS = [
                'localhost',
                '127.0.0.1',
                '192.168.10.18',
                '192.168.10.95',
               ' driving-licence-admin.vercel.app',
                'api.thegearup.ca',
                '192.168.10.20',
                'https://thegearup.ca'
                 ]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework.authtoken',
    'rest_framework',
    'corsheaders',
    'fcm_django',
    'utils_app',
    'admin_dashboard',
    'timing_slot_app',
    'user_management_app',
    'course_management_app',
    'django_celery_beat',

]



CORS_ORIGIN_WHITELIST = [
    'http://localhost:3000',
    'https://driving-licence-admin.vercel.app',
   'https://thegearup.ca'
]

CSRF_TRUSTED_ORIGINS = [
    'http://192.168.10.40:9000',
    'http://api.thegearup.ca',
    'https://api.thegearup.ca',
    'http://192.168.10.95:9000'

]

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'driving_license.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
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



WSGI_APPLICATION = 'driving_license.wsgi.application'

AUTH_USER_MODEL = "user_management_app.User"

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': os.getenv('ENGINE'),
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('HOST'),
        'PORT': os.getenv('DATABASE_PORT'),
        'CONN_MAX_AGE': 600,
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


MAX_UPLOAD_SIZE = 209715200  # 200 MB in bytes

DATA_UPLOAD_MAX_MEMORY_SIZE = MAX_UPLOAD_SIZE

REST_FRAMEWORK = {
 
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 3,
    'DEFAULT_MAX_PAGE_SIZE': 104857600,
  }


# cred = credentials.Certificate("cred/gearup-f9aa6-firebase-adminsdk-tfvhx-345813eaed.json")
cred = credentials.Certificate("cred/drivinglicese-761f3-firebase-adminsdk-fbsvc-c6a1429da3.json")
firebase_admin.initialize_app(cred)

DEFAULT_FILE_STORAGE = 'driving_license.custom_storage.CustomFileSystemStorage'
# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Karachi'

USE_I18N = True

USE_TZ = True


# Celery Setting # settings.py

CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'


# CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"
CELERY_TIMEZONE = "America/Winnipeg"
CELERY_ENABLE_UTC = True  
# CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERYD_POOL = 'prefork'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/


CELERY_BEAT_SCHEDULE = {
    'course_progrress': {
        'task': 'user_management_app.tasks.send_course_progress_notifications',
        'schedule': crontab(hour=10, minute=00),
    },
    'incomplete_profile': {
        'task': 'user_management_app.tasks.check_incomplete_profiles',
        # 'schedule': crontab(hour=19, minute=00),
        'schedule': crontab(minute='*/1'),
    },
    
    'send-day-before-reminders': {
        'task': 'user_management_app.tasks.send_lesson_reminder_day_before',
        'schedule': crontab(hour=20, minute=0),  
    },
    'send-5-min-reminders': {
        'task': 'user_management_app.tasks.send_lesson_reminder_5_min_before',
        'schedule': crontab(minute='*/5'),
    },
    'notification_one_hour_checks': {
        'task': 'user_management_app.tasks.notification_checks',
         'schedule': timedelta(hours=1),
    },
}

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# CKEDITOR_UPLOAD_PATH = "uploads/"

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_SIGNATURE_NAME = 's3v4'
AWS_S3_REGION_NAME = 'ca-central-1'
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL =  None
AWS_S3_VERIFY = True
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# AWS_STORAGE_2ND_BUCKET_NAME = os.getenv('AWS_STORAGE_2ND_BUCKET_NAME')

ACCOUNT_SID = os.getenv('ACCOUNT_SID')
AUTH_TOKEN = os.getenv('AUTH_TOKEN')

STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.office365.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
SITE_ID = 1


DOMAIN = 'http://127.0.0.1:8000'