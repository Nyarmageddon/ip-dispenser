# Локальные переменные, перезаписывающие стандартные из settings.py

DEBUG = True

ALLOWED_HOSTS = ["*"]

SECRET = "YfZuZY2yNe1Be3DUGOkz81uSYA6cdkShmuf9FKgFX93tU6pGVXTTSFtn4E6YiMCa"

STATIC_ROOT = ""

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "db_name",
        "USER": "user_name",
        "PASSWORD": "password",
        # Подключение к docker-compose
        "HOST": "db",
        "PORT": "3306",
        "OPTIONS": {
            "init_command": "SET default_storage_engine=INNODB",
        },
    }
}

TIME_ZONE = "Asia/Yekaterinburg"
