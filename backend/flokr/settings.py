"""
Django settings for flokr project.
"""

from pathlib import Path
from decouple import config, Csv
from datetime import timedelta
import dj_database_url
import os
import sys

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# GDAL Configuration for Windows
if sys.platform == 'win32':
    # Try to find GDAL in conda environment
    conda_prefix = os.environ.get('CONDA_PREFIX')
    if conda_prefix:
        conda_path = Path(conda_prefix)
        gdal_bin = conda_path / 'Library' / 'bin'
        gdal_data = conda_path / 'Library' / 'share' / 'gdal'
        proj_lib = conda_path / 'Library' / 'share' / 'proj'
        
        if gdal_bin.exists():
            # Add GDAL bin to PATH
            os.environ['PATH'] = str(gdal_bin) + os.pathsep + os.environ.get('PATH', '')
            
        if gdal_data.exists():
            os.environ['GDAL_DATA'] = str(gdal_data)
            
        if proj_lib.exists():
            os.environ['PROJ_LIB'] = str(proj_lib)
        
        # Try to set GDAL_LIBRARY_PATH
        gdal_dll = gdal_bin / 'gdal.dll'
        if gdal_dll.exists():
            GDAL_LIBRARY_PATH = str(gdal_dll)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-dev-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    
    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'drf_spectacular',
    'django_celery_beat',
    
    # Local apps
    'users',
    'inventory',
    'reservations',
    'hubs',
    'community',
    'partners',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'flokr.urls'

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

WSGI_APPLICATION = 'flokr.wsgi.application'

# Database
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default='postgresql://flokr_user:flokr_password@localhost:5432/flokr_db'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Use PostGIS engine for geospatial support
DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'

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

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'users.User'

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'user': '100/minute',
        'anon': '20/minute',
    }
}

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=config('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', default=60, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=config('JWT_REFRESH_TOKEN_LIFETIME_DAYS', default=7, cast=int)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",   # Next.js frontend
    "http://localhost:19006",  # Expo default port
    "http://localhost:19000",  # Expo alternative port
    "http://localhost:8081",   # React Native Metro
]

CORS_ALLOW_CREDENTIALS = True

# Celery Configuration
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Celery Beat Schedule (Periodic Tasks)
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    # Expire pending reservations every hour
    'expire-pending-reservations': {
        'task': 'reservations.expire_pending_reservations',
        'schedule': crontab(minute=0),  # Every hour at :00
        'options': {
            'expires': 3300,  # Task expires after 55 minutes
        }
    },
    # Send pickup reminders daily at 9 AM
    'send-pickup-reminders': {
        'task': 'reservations.send_pickup_reminders',
        'schedule': crontab(hour=9, minute=0),  # 9:00 AM daily
        'options': {
            'expires': 3600,  # Task expires after 1 hour
        }
    },
    # Send return reminders daily at 9 AM
    'send-return-reminders': {
        'task': 'reservations.send_return_reminders',
        'schedule': crontab(hour=9, minute=0),  # 9:00 AM daily
        'options': {
            'expires': 3600,
        }
    },
    # Send overdue reminders daily at 10 AM
    'send-overdue-reminders': {
        'task': 'reservations.send_overdue_reminders',
        'schedule': crontab(hour=10, minute=0),  # 10:00 AM daily
        'options': {
            'expires': 3600,
        }
    },
    # Generate daily report at 11 PM
    'generate-reservation-report': {
        'task': 'reservations.generate_reservation_report',
        'schedule': crontab(hour=23, minute=0),  # 11:00 PM daily
        'options': {
            'expires': 3600,
        }
    },
    # Cleanup old reservations weekly on Sunday at 2 AM
    'cleanup-old-reservations': {
        'task': 'reservations.cleanup_old_reservations',
        'schedule': crontab(hour=2, minute=0, day_of_week=0),  # Sunday 2:00 AM
        'options': {
            'expires': 7200,  # 2 hours
        }
    },
}

# Celery Task Configuration
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes hard limit
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes soft limit
CELERY_WORKER_PREFETCH_MULTIPLIER = 1  # Disable prefetching for long tasks
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000  # Restart worker after 1000 tasks

# Redis Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://localhost:6379/0'),
    }
}

# Email Configuration
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# Frontend URL (for password reset emails)
FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:3000')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@flokr.com')

# DRF Spectacular Settings (API Documentation)
SPECTACULAR_SETTINGS = {
    'TITLE': 'fLOKr Platform API',
    'DESCRIPTION': 'API for the fLOKr community resource sharing platform',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# Security Settings (for production)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
