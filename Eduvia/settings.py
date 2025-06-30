from pathlib import Path
import os
from decouple import config
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)  # False للإنتاج على Render

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default=['localhost', '127.0.0.1', '.onrender.com'], cast=lambda v: [s.strip() for s in v.split(',')])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'accounts.apps.AccountsConfig',
    'courses.apps.CoursesConfig',
    'pages',
    'chatbot',
    'competitions',
    'performance_analysis',
    'django_celery_beat',
    'projects',
    'channels',
    'skills_market',
    'mentorship',
    'workshops',
    # 'cloudinary',  # معطل في التطوير المحلي
    # 'cloudinary.storage',  # معطل في التطوير المحلي
]

ASGI_APPLICATION = 'Eduvia.asgi.application'

# إعداد Channels مع Redis للإنتاج
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [config('REDIS_URL', default='redis://localhost:6379')],
        },
    },
}

LOGIN_URL = '/accounts/login/'

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

ROOT_URLCONF = 'Eduvia.urls'
AUTH_USER_MODEL = 'accounts.User'

# إعدادات اللغة والتدويل
LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = True
LANGUAGES = [
    ('en', 'English'),
    ('ar', 'Arabic'),
]
LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

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

WSGI_APPLICATION = 'Eduvia.wsgi.application'

# إعداد قاعدة البيانات
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default='postgres://postgres:ELAHLYclub@1907@localhost:5432/eduvia'),
        conn_max_age=600,
        ssl_require=config('DATABASE_SSL', default=not config('DEBUG', default=False, cast=bool), cast=bool)  # SSL معطل في التطوير المحلي
    )
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

TIME_ZONE = 'Africa/Cairo'
USE_TZ = True

# إعدادات الملفات الثابتة
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# إعدادات ملفات الوسائط
DEFAULT_FILE_STORAGE = config('DEFAULT_FILE_STORAGE', default='django.core.files.storage.FileSystemStorage')
# إعدادات Cloudinary (للإنتاج فقط)
if not config('DEBUG', default=False, cast=bool):
    CLOUDINARY_STORAGE = {
        'CLOUDINARY_URL': config('CLOUDINARY_URL')
    }
    DEFAULT_FILE_STORAGE = 'cloudinary.storage.MediaCloudinaryStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# إعدادات CSRF وSession للأمان
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default=['http://127.0.0.1:8000', 'https://*.onrender.com'])
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=not config('DEBUG', default=False, cast=bool), cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=not config('DEBUG', default=False, cast=bool), cast=bool)

# إعدادات HTTPS للإنتاج
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=not config('DEBUG', default=False, cast=bool), cast=bool)
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=31536000, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# إعدادات مفتاح Gemini API
GEMINI_API_KEY = config('GEMINI_API_KEY', default=None)

# إعدادات البريد الإلكتروني
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='creativitycode78@gmail.com')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='Creativity Code <creativitycode78@gmail.com>')

# إعدادات السجل (Logging)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# تعليق CRONJOBS لأن Render يستخدم Cron Jobs منفصلة
# CRONJOBS = [
#     ('0 18 * * 6', 'performance_analysis.tasks.send_dashboard_report_to_all'),  # Every Saturday at 6 PM
# ]