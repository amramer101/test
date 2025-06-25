from django.apps import AppConfig


class SharedConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.shared"
    verbose_name = "Shared Utilities"

    def ready(self):
        """Initialize shared components when the app is ready."""
        pass
