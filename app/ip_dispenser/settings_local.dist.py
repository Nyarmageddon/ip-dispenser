# Локальные переменные, перезаписывающие стандартные из settings.py

DEBUG = False

ALLOWED_HOSTS = []

SECRET = None
if SECRET is None:
    raise RuntimeError()

STATIC_ROOT = ""

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "db_name",
        "USER": "user_name",
        "PASSWORD": "password",
        "HOST": "localhost",
        "PORT": "3306",
        "OPTIONS": {
            "init_command": "SET default_storage_engine=INNODB",
        },
    }
}

TIME_ZONE = "Asia/Yekaterinburg"
