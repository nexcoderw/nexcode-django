import os
from pathlib import Path
from urllib.parse import parse_qsl, unquote, urlparse

from django.core.exceptions import ImproperlyConfigured
from dotenv import dotenv_values, load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


def getenv_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on"}


def getenv_list(name, default=None):
    value = os.getenv(name)
    if value is None:
        return list(default or [])

    return [item.strip() for item in value.split(",") if item.strip()]


# Read the mode without overriding process variables or production-file priority.
local_mode = dotenv_values(BASE_DIR / ".env").get("DJANGO_ENV", "development")
DJANGO_ENV = os.getenv("DJANGO_ENV", local_mode or "development").strip().lower()
if DJANGO_ENV not in {"development", "production"}:
    raise ImproperlyConfigured("DJANGO_ENV must be development or production.")
ENV_FILES = [BASE_DIR / ".env"]
if DJANGO_ENV == "production":
    ENV_FILES = [BASE_DIR / ".env.production", BASE_DIR / ".env"]

for env_file in ENV_FILES:
    if env_file.exists():
        load_dotenv(env_file, override=False)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ImproperlyConfigured("SECRET_KEY must be set in the environment or .env file.")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = getenv_bool("DEBUG", DJANGO_ENV != "production")
if DJANGO_ENV == "production" and DEBUG:
    raise ImproperlyConfigured("DEBUG must be False in production.")

# Keep canonical URLs independent of incoming hosts and tracking parameters.
SITE_URL = os.getenv("SITE_URL", "https://nexcode.africa").rstrip("/")
site_origin = urlparse(SITE_URL)
if (
    site_origin.scheme != "https"
    or not site_origin.hostname
    or site_origin.path
    or site_origin.query
    or site_origin.fragment
    or site_origin.username
    or site_origin.password
):
    raise ImproperlyConfigured(
        "SITE_URL must be an HTTPS origin without a path or credentials."
    )
SEARCH_ENGINE_INDEXING = getenv_bool(
    "SEARCH_ENGINE_INDEXING", DJANGO_ENV == "production" and not DEBUG
)

default_allowed_hosts = ["localhost", "127.0.0.1"]
if not DEBUG:
    default_allowed_hosts.extend(["nexcode.africa", "www.nexcode.africa"])

ALLOWED_HOSTS = getenv_list("ALLOWED_HOSTS", default_allowed_hosts)

default_csrf_trusted_origins = []
if not DEBUG:
    default_csrf_trusted_origins = [
        f"https://{host}"
        for host in ALLOWED_HOSTS
        if host and host != "*"
    ]

CSRF_TRUSTED_ORIGINS = getenv_list(
    "CSRF_TRUSTED_ORIGINS",
    default_csrf_trusted_origins,
)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
SECURE_SSL_REDIRECT = getenv_bool("SECURE_SSL_REDIRECT", not DEBUG)
SESSION_COOKIE_SECURE = getenv_bool("SESSION_COOKIE_SECURE", not DEBUG)
CSRF_COOKIE_SECURE = getenv_bool("CSRF_COOKIE_SECURE", not DEBUG)
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = os.getenv("SECURE_REFERRER_POLICY", "same-origin")
SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "0" if DEBUG else "31536000"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = getenv_bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", not DEBUG)
SECURE_HSTS_PRELOAD = getenv_bool("SECURE_HSTS_PRELOAD", not DEBUG)


# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',

    # Third party
    'taggit',
    'django.contrib.humanize',
    'whitenoise.runserver_nostatic',
    'ckeditor',
    'ckeditor_uploader',

    #Custom apps
    'home',
    'admin_api',
]

if DJANGO_ENV == "production":
    staticfiles_index = (
        INSTALLED_APPS.index(
            "django.contrib.staticfiles"
        )
    )

    INSTALLED_APPS.insert(
        staticfiles_index,
        "cloudinary_storage",
    )

    INSTALLED_APPS.append(
        "cloudinary"
    )

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

ROOT_URLCONF = 'nexcode.urls'

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

WSGI_APPLICATION = 'nexcode.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

database_url = os.getenv("DATABASE_URL", "").strip()

if not database_url:
    raise ImproperlyConfigured(
        "DATABASE_URL must be set to a PostgreSQL connection string."
    )

postgres_url = urlparse(database_url)
database_name = unquote(postgres_url.path.lstrip("/"))

if (
    postgres_url.scheme not in {"postgres", "postgresql"}
    or not postgres_url.hostname
    or not postgres_url.username
    or not postgres_url.password
    or not database_name
):
    raise ImproperlyConfigured(
        "DATABASE_URL must be a valid PostgreSQL connection string."
    )

try:
    database_port = postgres_url.port or 5432
    database_conn_max_age = int(
        os.getenv("DATABASE_CONN_MAX_AGE") or "30"
    )
except ValueError as error:
    raise ImproperlyConfigured(
        "DATABASE_URL port and DATABASE_CONN_MAX_AGE must be integers."
    ) from error

if database_conn_max_age < 0:
    raise ImproperlyConfigured(
        "DATABASE_CONN_MAX_AGE must be zero or greater."
    )

database_options = dict(parse_qsl(postgres_url.query))
database_options.setdefault("sslmode", "require")
using_transaction_pooler = "-pooler." in postgres_url.hostname

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": database_name,
        "USER": unquote(postgres_url.username),
        "PASSWORD": unquote(postgres_url.password),
        "HOST": postgres_url.hostname,
        "PORT": database_port,
        "OPTIONS": database_options,
        "CONN_MAX_AGE": database_conn_max_age,
        "CONN_HEALTH_CHECKS": True,
        "DISABLE_SERVER_SIDE_CURSORS": using_transaction_pooler,
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


STORAGES = {
    "default": {
        "BACKEND": (
            "django.core.files.storage."
            "FileSystemStorage"
        ),
    },
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage."
            "CompressedManifestStaticFilesStorage"
        ),
    },
}


if DJANGO_ENV == "production":
    CLOUDINARY_STORAGE = {
        "CLOUD_NAME": os.getenv(
            "CLOUDINARY_CLOUD_NAME"
        ),
        "API_KEY": os.getenv(
            "CLOUDINARY_API_KEY"
        ),
        "API_SECRET": os.getenv(
            "CLOUDINARY_API_SECRET"
        ),
        "SECURE": True,
    }

    if not all(
        (
            CLOUDINARY_STORAGE[
                "CLOUD_NAME"
            ],
            CLOUDINARY_STORAGE[
                "API_KEY"
            ],
            CLOUDINARY_STORAGE[
                "API_SECRET"
            ],
        )
    ):
        raise ImproperlyConfigured(
            "Production media storage requires "
            "CLOUDINARY_CLOUD_NAME, "
            "CLOUDINARY_API_KEY, and "
            "CLOUDINARY_API_SECRET."
        )

    STORAGES["default"] = {
        "BACKEND": (
            "cloudinary_storage.storage."
            "MediaCloudinaryStorage"
        ),
    }

# WhiteNoise for static files
WHITENOISE_AUTOREFRESH = DEBUG
WHITENOISE_USE_FINDERS = DEBUG

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

JAZZMIN_SETTINGS = {
    "site_title": "NEXCODE",
    "site_header": "NEXCODE",
    "site_brand": "NEXCODE",
    "welcome_sign": "Nexcode Admin Login",
    "show_sidebar": True,
    "navigation_expanded": True,
    "order_with_respect_to": ["auth", "books", "books.author", "books.book"],
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
    },
    "custom_css": "css/jazzmin.css",
    "custom_js": None,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": True,
    "sidebar_fixed": True,
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": True,
    "sidebar_nav_flat_style": False,
    "theme": "simplex",
    "show_ui_builder": True,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {"auth.user": "collapsible", "auth.group": "vertical_tabs"},
    "related_modal_active": False,
}

CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_IMAGE_BACKEND = "pillow"

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink'],
            ['RemoveFormat', 'Source'],
            ['Image', 'Table', 'HorizontalRule', 'SpecialChar'],
            ['Format', 'FontSize'],
            ['TextColor', 'BGColor'],
            ['Maximize', 'ShowBlocks'],
        ],
        'width': '100%',
        'height': 300,
        'removePlugins': 'stylesheetparser',
        'extraPlugins': 'image2',
        'image2_alignClasses': ['image-left', 'image-center', 'image-right'],
        'image2_disableResizer': False,
    },
}

# -----------------------------------------------------------------------------
# Email
# -----------------------------------------------------------------------------

EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    (
        "django.core.mail.backends.console.EmailBackend"
        if DEBUG
        else "django.core.mail.backends.smtp.EmailBackend"
    ),
)

EMAIL_HOST = os.getenv(
    "EMAIL_HOST",
    "",
)

EMAIL_PORT = int(
    os.getenv(
        "EMAIL_PORT",
        "587",
    )
)

EMAIL_HOST_USER = os.getenv(
    "EMAIL_HOST_USER",
    "",
)

EMAIL_HOST_PASSWORD = os.getenv(
    "EMAIL_HOST_PASSWORD",
    "",
)

EMAIL_USE_TLS = getenv_bool(
    "EMAIL_USE_TLS",
    True,
)

DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL",
    (
        "NEXCODE <no-reply@localhost>"
        if DEBUG
        else ""
    ),
)

if (
    not DEBUG
    and EMAIL_BACKEND
    == "django.core.mail.backends.smtp.EmailBackend"
):
    if not EMAIL_HOST:
        raise ImproperlyConfigured(
            "EMAIL_HOST must be configured "
            "for production email."
        )

    if not DEFAULT_FROM_EMAIL:
        raise ImproperlyConfigured(
            "DEFAULT_FROM_EMAIL must be "
            "configured for production email."
        )
