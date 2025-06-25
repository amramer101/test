"""
Authorization Domain Package

This package handles all authorization and access control functionality including:
- Role-Based Access Control (RBAC) implementation
- Permission management and assignment
- Object-level permissions with django-guardian
- Role definitions and hierarchies
- Access control policies and rules
- Permission checking and enforcement

The authorization domain is responsible for determining what authenticated
users are allowed to do within the platform based on their roles and permissions.

Components:
- models.py: Role, Permission, and RBAC models
- serializers.py: Authorization data serialization
- views.py: Authorization management API endpoints
- services.py: RBAC business logic and permission checking
- permissions.py: Custom permission classes and decorators
- urls.py: Authorization URL routing
- managers.py: Custom model managers for permission queries
"""

default_app_config = "apps.authorization.apps.AuthorizationConfig"
