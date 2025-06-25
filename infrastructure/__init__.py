"""
RM Platform Infrastructure Package

This package contains infrastructure-related components that handle external
concerns and provide concrete implementations for the application's technical
requirements.

The infrastructure layer is responsible for:
- Database connections and configurations
- External service integrations
- Caching implementations
- Email service configurations
- File storage implementations
- Monitoring and logging setup
- Third-party API integrations

Components:
- database.py: Database configuration and connection management
- cache.py: Cache configuration and Redis/Valkey setup
- email.py: Email service configuration and implementations
- storage.py: File storage configuration (local/cloud)
- monitoring.py: Application monitoring and metrics
- external_services.py: Third-party service integrations
- security.py: Security-related infrastructure components

This layer implements the interfaces defined in the domain layer and provides
the technical infrastructure needed to support the application's business logic.
The infrastructure layer depends on the domain layer but the domain layer
should not depend on infrastructure components.
"""
