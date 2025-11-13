# config/settings.py
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# dev-only secret key; real projects: keep in env
SECRET_KEY = "dev-only-key"
DEBUG = True
ALLOWED_HOSTS = ["*"]  # dev: allow everything

# 1) add our apps (DRF, CORS, and our 'core')
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # third-party
    "rest_framework",        # Django REST Framework (API utilities)
    "corsheaders",           # so the React dev server can call our API

    # local app
    "core",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # must be near top so CORS headers are added
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],  # we’re not using server-side HTML templates for MVP
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": [
            "django.template.context_processors.debug",
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        ]},
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# 2) database: start simple with SQLite (no installation needed)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # file in your project root
    }
}

# 3) static files (not really used in this API-only MVP)
STATIC_URL = "static/"

# 4) DRF: no auth for MVP; you can add later
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "UNAUTHENTICATED_USER": None,
}

# 5) CORS: allow local React dev server to talk to us
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vite default
    "http://127.0.0.1:5173",
]
