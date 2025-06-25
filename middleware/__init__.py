"""
RM Platform Middleware Package

This package contains custom middleware components that handle cross-cutting
concerns throughout the application request/response cycle.

The middleware package provides:
- Security-related middleware for headers and protection
- Request/response logging and monitoring
- Rate limiting and throttling enforcement
- Performance monitoring and metrics collection
- Error handling and exception processing
- API versioning and content negotiation
- Custom authentication and authorization middleware

Components:
- security.py: Security headers, CSP, and protection middleware
- logging.py: Request/response logging and audit trail middleware
- rate_limiting.py: API rate limiting and throttling middleware
- monitoring.py: Performance monitoring and metrics collection
- error_handling.py: Custom error handling and response formatting
- versioning.py: API versioning and backward compatibility
- cors.py: Enhanced CORS handling for different environments
- compression.py: Response compression and optimization

Middleware Order Considerations:
The order of middleware in Django settings is important. This package
follows these guidelines:
1. Security middleware first (CORS, security headers)
2. Authentication and authorization middleware
3. Logging and monitoring middleware
4. Rate limiting and throttling
5. Error handling and response formatting
6. Performance optimization (compression, caching)

Each middleware component is designed to be:
- Lightweight and performant
- Configurable through Django settings
- Environment-aware (development vs production)
- Thoroughly tested and documented
- Compatible with both WSGI and ASGI applications
"""
