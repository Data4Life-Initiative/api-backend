import json
import logging
import os
from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from django.core.exceptions import ImproperlyConfigured

with open(os.path.join(BASE_DIR, 'resources/configuration',
                       os.environ.setdefault('DATA4LIFE_CONFIG', 'config-development.json'))) as f:
    configs = json.loads(f.read())


def get_env_var(setting, configs=configs):
    try:
        val = configs[setting]
        if val == 'True':
            val = True
        elif val == 'False':
            val = False
        return val
    except KeyError:
        error_msg = "ImproperlyConfigured: Unable to fetch value for key: {0} from configuration".format(setting)
        raise ImproperlyConfigured(error_msg)


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'rest_framework',
    'core.apps.CoreConfig',
    'authentication.apps.AuthenticationConfig',
    'dashboard.apps.DashboardConfig',
    'patient.apps.PatientConfig',
    'citizen.apps.CitizenConfig',
    'disease.apps.DiseaseConfig',
    'super_admin.apps.SuperAdminConfig',
    'push_notifications'
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

ROOT_URLCONF = 'data4life_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
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

WSGI_APPLICATION = 'data4life_backend.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = get_env_var('STATIC_FILES_URL')
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_TMP = os.path.join(BASE_DIR, "static")
UPLOADS_TMP = os.path.join(BASE_DIR, 'static/uploads/')

os.makedirs(STATIC_TMP, exist_ok=True)
os.makedirs(UPLOADS_TMP, exist_ok=True)

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static")
]

# Default file storage settings
UPLOADS_LOCATION = os.path.join(BASE_DIR, 'static/uploads/')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'access': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'access.log',
            'formatter': 'verbose'
        },
        'error': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': 'error.log',
            'formatter': 'verbose'
        },
        'debug': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'info': {
            'handlers': ['access'],
            'level': 'INFO',
        },
        'error': {
            'handlers': ['error'],
            'level': 'ERROR',
        },
        'debug': {
            'handlers': ['debug'],
            'level': 'DEBUG',
        }
    }
}

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'core.exceptions.core_exception_handler',
    'NON_FIELD_ERRORS_KEY': 'error',
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'core.custom_authentication_class.KeycloakAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ]
}

AUTH_USER_MODEL = 'authentication.User'

DEBUG = get_env_var('DEBUG')

ALLOWED_HOSTS = ["*"]

# Databases configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': get_env_var("DATABASE")["NAME"],
        'USER': get_env_var("DATABASE")["USER"],
        'PASSWORD': get_env_var("DATABASE")["PASSWORD"],
        'HOST': get_env_var("DATABASE")["HOST"],
        'PORT': get_env_var("DATABASE")["PORT"]
    },
}

SECRET_KEY = get_env_var("SECRET_KEY")

# JWT token authentication configuration for rest_framework_simplejwt package
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=int(get_env_var("ACCESS_TOKEN_LIFETIME")["minutes"])),
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=int(get_env_var("REFRESH_TOKEN_LIFETIME")["minutes"])),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# Twilio configuration
TWILIO_MOBILE_NUMBER = get_env_var("TWILIO")["MOBILE_NUMBER"]
TWILIO_ACCOUNT_ID = get_env_var("TWILIO")["ACCOUNT_ID"]
TWILIO_TOKEN = get_env_var("TWILIO")["TOKEN"]

# One time password SMS message format
OTP_MESSAGE = get_env_var("OTP_MESSAGE")

# Super admins list for initializing database
SUPER_ADMINS = get_env_var("SUPER_ADMINS")

# configuring loggers
LOGGER_DEBUG = logging.getLogger('debug')
LOGGER_INFO = logging.getLogger('info')
LOGGER_ERROR = logging.getLogger('error')

# data4life configuration

# patient historic location expiry duration
HISTORIC_LOCATION_EXPIRY_IN_SECONDS = int(get_env_var("HISTORIC_LOCATION_EXPIRY_IN_SECONDS"))

# QR code URL for patients to scan and sync their historic location after obtaining explicit consent
HISTORIC_LOCATION_SYNC_CONSENT_QR_CODE_URL = get_env_var('HISTORIC_LOCATION_SYNC_CONSENT_QR_CODE_URL')

# proximity notifications

# if the citizen location is within the proximity of `x` meters then trigger proximity notification
HOTSPOT_PROXIMITY_IN_METRES = int(get_env_var("HOTSPOT_PROXIMITY_NOTIFICATIONS")["PROXIMITY_IN_METRES"])

# In order to avoid spamming citizens with notifications, a delay is attached to it
# if time elapsed after the last notification is greater than the below delay in seconds,
# then notification is safe to trigger
DELAY_BETWEEN_NOTIFICATIONS_IN_SECONDS = int(
    get_env_var("HOTSPOT_PROXIMITY_NOTIFICATIONS")["DELAY_BETWEEN_NOTIFICATIONS_IN_SECONDS"])

# data4life IAM configuration
# Access token decoding using RSA public key
RSA_KEYS = get_env_var('IAM')['RSA_KEYS']
IAM_REALM = get_env_var('IAM')['REALM']
IAM_URL = get_env_var('IAM')['URL']
IAM_ADMIN_USERNAME = get_env_var('IAM')['ADMIN_USERNAME']
IAM_ADMIN_PASSWORD = get_env_var('IAM')['ADMIN_PASSWORD']

# push notification configuration
PUSH_NOTIFICATIONS_SETTINGS = {
    "FCM_API_KEY": get_env_var("PUSH_NOTIFICATIONS_SETTINGS")['FCM_API_KEY'],
    "GCM_API_KEY": get_env_var("PUSH_NOTIFICATIONS_SETTINGS")['GCM_API_KEY'],
    "APNS_CERTIFICATE": get_env_var("PUSH_NOTIFICATIONS_SETTINGS")["APNS_CERTIFICATE"],
    "APNS_TOPIC": get_env_var("PUSH_NOTIFICATIONS_SETTINGS")["APNS_TOPIC"]
}
