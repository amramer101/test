"""
RM Platform Core Package

This package contains the core domain logic and fundamental business entities
that form the foundation of the RM Platform application.

The core package follows Domain-Driven Design principles and contains:
- Domain models and entities
- Core business services and logic
- Domain exceptions and value objects
- Shared business rules and validations

This package is independent of external frameworks and focuses purely on
business logic, making it highly testable and maintainable.

Components:
- models.py: Core domain models and business entities
- services.py: Core business services and domain logic
- exceptions.py: Domain-specific exceptions
- value_objects.py: Value objects and domain primitives
- repositories.py: Abstract repository interfaces
- events.py: Domain events and event handling

The core package should have minimal dependencies and should not import
from apps or infrastructure packages to maintain clean architecture boundaries.
"""

default_app_config = "core.apps.CoreConfig"
