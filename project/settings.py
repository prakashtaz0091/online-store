from pathlib import Path
import os
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("DJANGO_SECRET")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", cast=bool)

ALLOWED_HOSTS = ["d6c18ba958c5.ngrok-free.app", "*"]

CSRF_TRUSTED_ORIGINS = [
    "https://d6c18ba958c5.ngrok-free.app",
    "https://*.ngrok-free.app",
    "https://*.ngrok.io",
]

# Application definition

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "store",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "accounts.middlewares.RedirectIfAuthenticatedMiddleware",
    "accounts.middlewares.AdminRequiredMiddleware",
]

INTERNAL_IPS = [
    # ...
    "127.0.0.1",
    # ...
]

ROOT_URLCONF = "project.urls"
AUTH_USER_MODEL = "accounts.CustomUser"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "common_templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "project.wsgi.application"


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
    # "default": {
    #     "ENGINE": "django.db.backends.postgresql",
    #     "NAME": config("DB_NAME"),
    #     "USER": config("DB_USER"),
    #     "PASSWORD": config("DB_PASSWORD"),
    #     "HOST": config("DB_HOST"),  # Use 'localhost' for a local PostgreSQL instance
    #     "PORT": config(
    #         "DB_PORT"
    #     ),  # Leave empty to use the default PostgreSQL port (5432)
    # }
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = "en-us"

# TIME_ZONE = "UTC"
TIME_ZONE = "Asia/Kathmandu"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = "static/"


MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"

KHALTI_BASE_URL = config("KHALTI_BASE_URL")
KHALTI_SECRET_KEY = config("KHALTI_SECRET_KEY")
SITE_URL = "http://localhost:8000"


########### JAZZMIN settings #######################
JAZZMIN_SETTINGS = {
    # title of the window (Will default to current_admin_site.site_title if absent or None)
    "site_title": "Online Store Admin",
    # Title on the login screen (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_header": "Online Store",
    # Title on the brand (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_brand": "Online Store",
    # Logo to use for your site, must be present in static files, used for brand on top left
    # Logo to use for your site, must be present in static files, used for login form logo (defaults to site_logo)
    "login_logo": None,
    # Logo to use for login form in dark themes (defaults to login_logo)
    "login_logo_dark": None,
    # CSS classes that are applied to the logo above
    "site_logo_classes": "img-circle",
    # Relative path to a favicon for your site, will default to site_logo if absent (ideally 32x32 px)
    "site_icon": None,
    # Welcome text on the login screen
    "welcome_sign": "Welcome to the library",
    # Copyright on the footer
    "copyright": "Acme Library Ltd",
    # List of model admins to search from the search bar, search bar omitted if excluded
    #############
    # Side Menu #
    #############
    # Whether to display the side menu
    "show_sidebar": True,
    # Whether to aut expand the menu
    "navigation_expanded": True,
    # Hide these apps when generating side menu e.g (auth)
    "hide_apps": [],
    # Hide these models when generating side menu (e.g auth.user)
    "hide_models": [],
    # List of apps (and/or models) to base side menu ordering off of (does not need to contain all apps/models)
    "order_with_respect_to": ["auth", "books", "books.author", "books.book"],
    # Custom links to append to app groups, keyed on app name
    # Custom icons for side menu apps/models See https://fontawesome.com/icons?d=gallery&m=free&v=5.0.0,5.0.1,5.0.10,5.0.11,5.0.12,5.0.13,5.0.2,5.0.3,5.0.4,5.0.5,5.0.6,5.0.7,5.0.8,5.0.9,5.1.0,5.1.1,5.2.0,5.3.0,5.3.1,5.4.0,5.4.1,5.4.2,5.13.0,5.12.0,5.11.2,5.11.1,5.10.0,5.9.0,5.8.2,5.8.1,5.7.2,5.7.1,5.7.0,5.6.3,5.5.0,5.4.2
    # for the full list of 5.13.0 free icon classes
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
    },
    # Icons that are used when one is not manually specified
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    #################
    # Related Modal #
    #################
    # Use modals instead of popups
    "related_modal_active": False,
    #############
    # UI Tweaks #
    #############
    # Relative paths to custom CSS/JS scripts (must be present in static files)
    "custom_css": None,
    "custom_js": None,
    # Whether to link font from fonts.googleapis.com (use custom_css to supply font otherwise)
    "use_google_fonts_cdn": True,
    # Whether to show the UI customizer on the sidebar
    "show_ui_builder": True,
    ###############
    # Change view #
    ###############
    # Render out the change view as a single form, or in tabs, current options are
    # - single
    # - horizontal_tabs (default)
    # - vertical_tabs
    # - collapsible
    # - carousel
    "changeform_format": "horizontal_tabs",
    # override change forms on a per modeladmin basis
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs",
    },
    # Add a language dropdown into the admin
}


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "logs/django.log"),
            "maxBytes": 1024 * 1024 * 15,  # 15MB
            "backupCount": 10,
            "formatter": "verbose",
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file", "console"],
            "level": "INFO",
            "propagate": True,
        },
        "accounts": {
            "handlers": ["file", "console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}


# mailhog email for testing
# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_HOST = "localhost"
# EMAIL_PORT = 1025
# DEFAULT_FROM_EMAIL = "test@example.com"


# real email for production
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"  # or "smtp.office365.com" or any other email provider
EMAIL_PORT = 587  # according to your email provider
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True  # use if your email provider doesn't support SSL and supports TLS

# EMAIL_USE_SSL = False # keep True if your email provider doesn't support TLS and supports SSL
# Note: TLS and SSL are mutually exclusive and they are used for security purposes (e.g. encryption, for privacy)
