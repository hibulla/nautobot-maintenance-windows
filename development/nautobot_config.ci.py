"""Nautobot configuration used by GitHub Actions integration tests."""

import os

from nautobot.core.settings import *  # noqa: F403

ALLOWED_HOSTS = ["*"]
SECRET_KEY = os.environ.get("NAUTOBOT_SECRET_KEY", "ci-only-secret-key-not-for-production")
DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("NAUTOBOT_DB_NAME", "nautobot"),
        "USER": os.environ.get("NAUTOBOT_DB_USER", "nautobot"),
        "PASSWORD": os.environ.get("NAUTOBOT_DB_PASSWORD", "nautobot"),
        "HOST": os.environ.get("NAUTOBOT_DB_HOST", "postgres"),
        "PORT": os.environ.get("NAUTOBOT_DB_PORT", "5432"),
        "CONN_MAX_AGE": int(os.environ.get("NAUTOBOT_DB_TIMEOUT", "300")),
    }
}

REDIS_HOST = os.environ.get("NAUTOBOT_REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("NAUTOBOT_REDIS_PORT", "6379"))
REDIS_PASSWORD = os.environ.get("NAUTOBOT_REDIS_PASSWORD", "")

REDIS = {
    "tasks": {
        "HOST": REDIS_HOST,
        "PORT": REDIS_PORT,
        "PASSWORD": REDIS_PASSWORD,
        "DATABASE": 0,
        "SSL": False,
    },
    "caching": {
        "HOST": REDIS_HOST,
        "PORT": REDIS_PORT,
        "PASSWORD": REDIS_PASSWORD,
        "DATABASE": 1,
        "SSL": False,
    },
}

CACHEOPS_REDIS = {
    "host": REDIS_HOST,
    "port": REDIS_PORT,
    "db": 1,
    "password": REDIS_PASSWORD,
    "ssl": False,
}

PLUGINS = ["nautobot_maintenance_windows"]
PLUGINS_CONFIG = {}
