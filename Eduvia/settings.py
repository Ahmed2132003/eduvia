from pathlib import Path
import sys
import os
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-hfxyoz#%!ei3v1zfmj5km20vkx$$tvm$)7$0r_79h2k+wbuki^')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '*.fly.dev',
    'eduvia-ai.fly.dev',
    '75727303c9c8.ngrok-free.app',
]
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'https://*.fly.dev',
    'https://eduvia-ai.fly.dev',
    'https://75727303c9c8.ngrok-free.app',
]

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
    'competitions',
    'performance_analysis',
    'django_celery_beat',
    'projects',
    'channels',
    'skills_market',
    'mentorship',
    'workshops',
    'widget_tweaks',
    'rest_framework',
    'marketplace.apps.MarketplaceConfig',
    'groups',

]

ASGI_APPLICATION = 'Eduvia.asgi.application'

CELERY_BROKER_URL = config('REDIS_URL', default='redis://localhost:6379')
CELERY_RESULT_BACKEND = config('REDIS_URL', default='redis://localhost:6379')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

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
    'marketplace.middleware.StudentAccessMiddleware',
]

ROOT_URLCONF = 'Eduvia.urls'
AUTH_USER_MODEL = 'accounts.User'

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
        'DIRS': [BASE_DIR / 'templates',
            BASE_DIR / 'skills_market/templates',],
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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': config('DATABASE_PATH', default=str(BASE_DIR / 'db.sqlite3')),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

TIME_ZONE = 'Africa/Cairo'
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = '/data/media'

SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=False, cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=False, cast=bool)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=0, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

GEMINI_API_KEY = config('GEMINI_API_KEY', default=None)

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='creativitycode78@gmail.com')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='Creativity Code <creativitycode78@gmail.com>')

# ---------------------------------------------------------------------------
# Part 23 (المرحلة الثانية — البث المباشر): إعدادات مزود الـ WebRTC
# (LiveKit). القرار المعماري الكامل لاختيار LiveKit تحديدًا موثق في
# PROGRESS_PART22.md (Part 22).
#
# قرار: استخدمت نفس أسلوب config() من python-decouple المستخدم في كل
# سطر حساس تاني في الملف ده (SECRET_KEY، REDIS_URL، EMAIL_HOST_PASSWORD
# فوق)، بدل os.environ.get المباشرة المقترحة حرفيًا في نص خطة المرحلة
# الثانية — عشان الاتساق مع الملف ده بالكامل أهم من اتباع الصياغة
# الحرفية، ونفس السلوك العملي (قراءة من متغير بيئة + قيمة افتراضية) بيتحقق
# بالظبط بالطريقتين.
#
# القيم الافتراضية فاضية عمدًا — مفيش أي مفتاح/سيكرت حقيقي مكتوب هنا في
# الكود. لازم تتظبط فعليًا كمتغيرات بيئة (.env محليًا، أو إعدادات
# السيرفر/الاستضافة) قبل ما groups/live_provider.py يقدر يشتغل فعليًا —
# لو مش متظبطة، الدوال هناك بترمي LiveProviderError واضح بدل ما تفشل
# بغموض.
#
# LIVEKIT_URL بيختلف حسب قرار الاستضافة (self-hosted بـ Docker أو
# LiveKit Cloud) — القرار ده تشغيلي بحت (Ahmed هو اللي هيحدده وقت
# النشر الفعلي)، وكود groups/live_provider.py نفسه مبيتغيرش في الحالتين،
# الفرق كله في قيمة اللينك ده بس:
#   - self-hosted (Docker):  LIVEKIT_URL=ws://localhost:7880  (أو
#     العنوان الداخلي لكونتينر LiveKit على السيرفر)
#   - LiveKit Cloud:         LIVEKIT_URL=wss://<project>.livekit.cloud
LIVEKIT_URL = config('LIVEKIT_URL', default='')
LIVEKIT_API_KEY = config('LIVEKIT_API_KEY', default='')
LIVEKIT_API_SECRET = config('LIVEKIT_API_SECRET', default='')

# ---------------------------------------------------------------------------
# Part 26 (نسخة معدّلة — Manual Recording Upload): كان هنا 6 إعدادات
# S3-compatible مخصصة لـ LiveKit Egress (LIVEKIT_EGRESS_S3_*) — اتشالت
# بالكامل لإن نظام التسجيل التلقائي (Egress -> S3) اتلغى تمامًا. التسجيل
# بقى بيتم برفع يدوي من المدرس، باستخدام نفس Storage المحلي المظبوط فوق
# (DEFAULT_FILE_STORAGE / MEDIA_ROOT) — بدون أي مخزن S3 منفصل.
#
# الحد الأقصى لحجم فيديو التسجيل اللي المدرس بيرفعه يدويًا بعد ما اللايف
# يخلص (groups/views.py::upload_group_recording). نفس أسلوب config()
# زي باقي الإعدادات في الملف ده. القيمة بالميجابايت (أسهل للقراءة/التعديل)
# وبتتحول لبايت وقت التحقق الفعلي في groups/views.py. 1024 ميجا (1 جيجا)
# قيمة افتراضية معقولة اخترتها بنفسي — الطلب الأصلي قال "حسب إعدادات
# المشروع" من غير رقم محدد، فسهل تتغير من هنا لو Ahmed عايز حد مختلف.
GROUP_LIVE_RECORDING_MAX_UPLOAD_MB = config(
    'GROUP_LIVE_RECORDING_MAX_UPLOAD_MB', default=1024, cast=int,
)


if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='backslashreplace')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
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