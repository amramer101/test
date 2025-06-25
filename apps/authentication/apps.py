from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.authentication"
    verbose_name = "Authentication"

    def ready(self):
        """
        Initialize authentication components when the app is ready.
        """
        # Import signal handlers
        try:
            from . import signals
        except ImportError:
            pass

        # Initialize authentication services
        self._initialize_auth_services()

    def _initialize_auth_services(self):
        """
        Initialize authentication-related services and components.
        """
        # Initialize JWT token handlers, custom authentication backends, etc.
        pass
