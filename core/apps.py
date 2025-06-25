from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    verbose_name = "Core Domain"

    def ready(self):
        """
        Initialize core components when the app is ready.
        This method is called when Django starts up.
        """
        # Import signal handlers
        try:
            from . import signals
        except ImportError:
            pass

        # Initialize domain services
        self._initialize_domain_services()

        # Register domain events
        self._register_domain_events()

    def _initialize_domain_services(self):
        """
        Initialize core domain services.
        """
        # Initialize any singleton services or domain registries here
        pass

    def _register_domain_events(self):
        """
        Register domain event handlers.
        """
        # Register domain event handlers here
        pass
