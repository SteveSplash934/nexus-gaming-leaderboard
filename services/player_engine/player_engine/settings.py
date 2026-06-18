import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "nexus-player-engine-insecure-key"
DEBUG = True
ALLOWED_HOSTS = ["*"]

# Stripped down to only what is needed for a DB-backed API
INSTALLED_APPS = [
    "players.apps.PlayersConfig",
]

MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "player_engine.urls"

# Dynamic Database Path Routing (Local vs Docker Volume)
DB_DIR = Path("/app/data") if Path("/app/data").exists() else BASE_DIR

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DB_DIR / "players.sqlite3",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
