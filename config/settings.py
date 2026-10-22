import os
from pathlib import Path

from django.urls import reverse_lazy

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-change-me-in-production")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
CSRF_TRUSTED_ORIGINS = [o for o in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if o]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

INSTALLED_APPS = [
    "unfold",  # современная админка, должна идти перед django.contrib.admin
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",
]

MIDDLEWARE = [
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
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.site",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "ru"
TIME_ZONE = "Asia/Tashkent"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---- Админка (django-unfold) ----
UNFOLD = {
    "SITE_TITLE": "Coloroom Interiors",
    "SITE_HEADER": "Coloroom Interiors",
    "SITE_SYMBOL": "chair",
    "SITE_URL": "/",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "COLORS": {
        "primary": {
            "50": "248 244 240",
            "100": "238 229 220",
            "200": "221 205 191",
            "300": "200 177 157",
            "400": "176 146 121",
            "500": "153 122 96",
            "600": "128 100 78",
            "700": "104 82 65",
            "800": "86 69 56",
            "900": "72 58 49",
            "950": "40 32 27",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Контент сайта",
                "separator": True,
                "items": [
                    {"title": "Проекты", "icon": "photo_library",
                     "link": reverse_lazy("admin:core_project_changelist")},
                    {"title": "Категории проектов", "icon": "category",
                     "link": reverse_lazy("admin:core_category_changelist")},
                    {"title": "Страница «Проекты»", "icon": "web",
                     "link": reverse_lazy("admin:core_projectspage_changelist")},
                    {"title": "Главная и подвал", "icon": "tune",
                     "link": reverse_lazy("admin:core_sitesettings_changelist")},
                    {"title": "Страница «О нас»", "icon": "info",
                     "link": reverse_lazy("admin:core_aboutpage_changelist")},
                    {"title": "Контакты в подвале", "icon": "contacts",
                     "link": reverse_lazy("admin:core_contactblock_changelist")},
                ],
            },
            {
                "title": "Навигация",
                "separator": True,
                "items": [
                    {"title": "Меню сайта", "icon": "menu",
                     "link": reverse_lazy("admin:core_menuitem_changelist")},
                ],
            },
            {
                "title": "Обращения",
                "separator": True,
                "items": [
                    {"title": "Заявки с сайта", "icon": "mail",
                     "link": reverse_lazy("admin:core_contactrequest_changelist")},
                ],
            },
            {
                "title": "Доступ",
                "separator": True,
                "items": [
                    {"title": "Пользователи", "icon": "person",
                     "link": reverse_lazy("admin:auth_user_changelist")},
                ],
            },
        ],
    },
}
