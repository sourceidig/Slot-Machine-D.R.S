"""
Settings para ejecutar tests localmente sin MariaDB (usa SQLite en memoria).
Uso: python manage.py test control --settings=slot_machine_drs.settings_test
"""
from .settings import *  # noqa: F401, F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

DEBUG = True

# Eliminar ErrorHandlerMiddleware en tests: convierte PermissionDenied en 500
# impidiendo verificar respuestas 403. Django maneja PermissionDenied como 403
# de forma nativa cuando este middleware no interfiere.
MIDDLEWARE = [m for m in MIDDLEWARE if "ErrorHandlerMiddleware" not in m]
