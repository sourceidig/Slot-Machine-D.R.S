from django.apps import AppConfig


class ControlConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'control'
    verbose_name = 'Sistema de Control de Máquinas'

    def ready(self):
        import control.signals  # noqa: F401 — conectar señales de audit log
