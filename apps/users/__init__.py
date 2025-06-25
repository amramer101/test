"""
Users Domain Package

This package handles all user management functionality including:
- User model and profile management
- User registration and account creation
- User profile updates and preferences
- User-related business logic and services
- User permissions and role assignments

The users domain represents the core user entity and all operations
related to user lifecycle management within the platform.

Components:
- models.py: User model and related entities
- serializers.py: User data serialization and validation
- views.py: User management API endpoints
- services.py: User business logic and operations
- repositories.py: User data access patterns
- permissions.py: User-specific permissions
- urls.py: User management URL routing
"""

default_app_config = "apps.users.apps.UsersConfig"
