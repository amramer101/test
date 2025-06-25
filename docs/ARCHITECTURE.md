# RM Platform Architecture

## Overview
The RM Platform is designed using Domain-Driven Design (DDD) principles, modular Django apps, and a layered architecture. It aims for scalability, maintainability, and clear separation of concerns.

## Key Patterns
- **Domain Models**: Encapsulate business logic, but must be integrated with Django ORM for persistence.
- **BaseModel**: Shared abstract model for UUID PK, timestamps, audit, and soft delete fields.
- **Soft Delete**: Implemented via `is_deleted` and `deleted_at` fields, with a custom manager/queryset.
- **JWT Authentication**: Centralized in `apps/authentication/infrastructure/jwt.py`.
- **RBAC**: Role-based access control in the `authorization` app.
- **Infrastructure Layer**: Shared utilities for email, cache, storage, and database.

## Architectural Decisions
- **Persistence**: All persistent data should use Django ORM models. Domain models are for business logic and should not duplicate ORM models.
- **Token Management**: Use database-backed models for password reset and email verification tokens.
- **Configuration**: All environment-specific settings are loaded from environment variables.
- **Testing**: Each app has its own test suite for models, views, and serializers.

## Recommendations
- Avoid duplicating logic between domain and ORM models.
- Use the shared `BaseModel` for all models requiring audit/soft delete fields.
- Integrate infrastructure utilities via Django management commands or admin interfaces.
- Document all architectural decisions in this file for future maintainers.

---
