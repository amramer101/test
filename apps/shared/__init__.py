"""
Shared Utilities Package

This package contains shared utilities, base classes, and common functionality
used across all domains in the RM Platform.

Components:
- models.py: Abstract base models with common fields
- serializers.py: Base serializers with common functionality
- permissions.py: Reusable permission classes (IsOwner, IsAdminOrReadOnly, permission_factory)
- exceptions.py: Custom exception classes and DRF exception handler
- validators.py: Custom field validators
- pagination.py: Custom pagination classes (page number, cursor)
- utils.py: General utility functions (random string, slug, validators, file helpers)

These shared components ensure consistency across the platform and
reduce code duplication while maintaining clean domain boundaries.
"""

default_app_config = "apps.shared.apps.SharedConfig"
