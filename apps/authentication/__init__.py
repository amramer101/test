"""
Authentication Domain Package

This package handles all authentication-related functionality including:
- JWT token authentication and management
- User login/logout operations
- Password reset and recovery
- Token refresh mechanisms
- Authentication middleware and decorators

The authentication domain is responsible for verifying user identity
and managing secure access to the platform through JWT tokens.

Components:
- models.py: Authentication-related models (if any)
- serializers.py: Authentication request/response serializers
- views.py: Authentication API endpoints
- services.py: Authentication business logic
- permissions.py: Authentication-specific permissions
- urls.py: Authentication URL routing
"""

default_app_config = "apps.authentication.apps.AuthenticationConfig"
