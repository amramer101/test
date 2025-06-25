"""
RM Platform Apps Package

This package contains all Django applications organized by domain following
Domain-Driven Architecture principles.

Structure:
- shared: Common utilities and base classes used across domains
- authentication: JWT authentication and session management
- users: User management and profile functionality
- authorization: Role-based access control (RBAC) and permissions
- products: Sample domain for demonstration purposes

Each app follows DDD patterns with:
- models.py: Domain entities and aggregates
- services.py: Application services and business logic
- repositories.py: Data access patterns (where applicable)
- serializers.py: API serialization and validation
- views.py: API controllers and interfaces
- permissions.py: Authorization and access control
- urls.py: URL routing and endpoint configuration
"""
