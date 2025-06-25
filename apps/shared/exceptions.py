from rest_framework import status
from rest_framework.views import exception_handler
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
import logging
from rest_framework.exceptions import APIException

logger = logging.getLogger(__name__)


class BaseAPIException(Exception):
    """
    Base exception class for all API-related exceptions.
    """

    default_message = "An error occurred"
    default_code = "error"
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, message=None, code=None, status_code=None, extra_data=None):
        self.message = message or self.default_message
        self.code = code or self.default_code
        self.status_code = status_code or self.status_code
        self.extra_data = extra_data or {}
        super().__init__(self.message)


class AuthenticationError(BaseAPIException):
    """
    Exception raised when authentication fails.
    """

    default_message = "Authentication failed"
    default_code = "authentication_failed"
    status_code = status.HTTP_401_UNAUTHORIZED


class AuthorizationError(BaseAPIException):
    """
    Exception raised when user doesn't have permission to perform action.
    """

    default_message = "You don't have permission to perform this action"
    default_code = "permission_denied"
    status_code = status.HTTP_403_FORBIDDEN


class ValidationAPIError(BaseAPIException):
    """
    Exception raised when data validation fails.
    """

    default_message = "Validation failed"
    default_code = "validation_error"
    status_code = status.HTTP_400_BAD_REQUEST


class NotFoundError(BaseAPIException):
    """
    Exception raised when requested resource is not found.
    """

    default_message = "Resource not found"
    default_code = "not_found"
    status_code = status.HTTP_404_NOT_FOUND


class ConflictError(BaseAPIException):
    """
    Exception raised when there's a conflict with current state.
    """

    default_message = "Conflict with current state"
    default_code = "conflict"
    status_code = status.HTTP_409_CONFLICT


class RateLimitError(BaseAPIException):
    """
    Exception raised when rate limit is exceeded.
    """

    default_message = "Rate limit exceeded"
    default_code = "rate_limit_exceeded"
    status_code = status.HTTP_429_TOO_MANY_REQUESTS


class ServiceUnavailableError(BaseAPIException):
    """
    Exception raised when service is temporarily unavailable.
    """

    default_message = "Service temporarily unavailable"
    default_code = "service_unavailable"
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE


class BusinessLogicError(BaseAPIException):
    """
    Exception raised when business logic rules are violated.
    """

    default_message = "Business logic error"
    default_code = "business_logic_error"
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY


class ExternalServiceError(BaseAPIException):
    """
    Exception raised when external service call fails.
    """

    default_message = "External service error"
    default_code = "external_service_error"
    status_code = status.HTTP_502_BAD_GATEWAY


class DatabaseError(BaseAPIException):
    """
    Exception raised when database operation fails.
    """

    default_message = "Database operation failed"
    default_code = "database_error"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class InvalidTokenError(AuthenticationError):
    """
    Exception raised when JWT token is invalid.
    """

    default_message = "Invalid or expired token"
    default_code = "invalid_token"


class TokenExpiredError(AuthenticationError):
    """
    Exception raised when JWT token has expired.
    """

    default_message = "Token has expired"
    default_code = "token_expired"


class InvalidCredentialsError(AuthenticationError):
    """
    Exception raised when login credentials are invalid.
    """

    default_message = "Invalid username or password"
    default_code = "invalid_credentials"


class AccountLockedError(AuthenticationError):
    """
    Exception raised when user account is locked.
    """

    default_message = "Account is locked due to too many failed login attempts"
    default_code = "account_locked"


class EmailNotVerifiedError(AuthenticationError):
    """
    Exception raised when user's email is not verified.
    """

    default_message = "Email address not verified"
    default_code = "email_not_verified"


class DuplicateResourceError(ConflictError):
    """
    Exception raised when trying to create duplicate resource.
    """

    default_message = "Resource already exists"
    default_code = "duplicate_resource"


class ResourceInUseError(ConflictError):
    """
    Exception raised when trying to delete resource that is in use.
    """

    default_message = "Resource is currently in use and cannot be deleted"
    default_code = "resource_in_use"


class InvalidOperationError(BusinessLogicError):
    """
    Exception raised when operation is not valid in current context.
    """

    default_message = "Operation not valid in current context"
    default_code = "invalid_operation"


class InsufficientFundsError(BusinessLogicError):
    """
    Example business logic exception for financial operations.
    """

    default_message = "Insufficient funds for this operation"
    default_code = "insufficient_funds"


class ConflictException(APIException):
    status_code = 409
    default_detail = "Conflict."
    default_code = "conflict"


class RateLimitException(APIException):
    status_code = 429
    default_detail = "Rate limit exceeded."
    default_code = "rate_limited"


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses and prevents sensitive information leakage.
    Handles JWT-related exceptions, logs security errors, and ensures stack traces are not exposed.
    """
    response = exception_handler(exc, context)
    if response is not None:
        # Hide stack traces and sensitive details
        if isinstance(response.data, dict):
            response.data.pop('traceback', None)
            response.data.pop('stack', None)
        # Standardize error format
        response.data = {
            'error': response.data.get('detail', str(exc)),
            'code': getattr(exc, 'default_code', 'error'),
            'status_code': response.status_code,
        }
    else:
        # Unhandled exceptions
        logger.exception("Unhandled exception: %s", exc)
        return exception_handler(Exception("Internal server error"), context)
    return response


def handle_database_error(func):
    """
    Decorator to handle database errors consistently.
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Database error in {func.__name__}: {e}")
            raise DatabaseError(f"Database operation failed: {str(e)}")

    return wrapper


def handle_external_service_error(func):
    """
    Decorator to handle external service errors consistently.
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"External service error in {func.__name__}: {e}")
            raise ExternalServiceError(f"External service call failed: {str(e)}")

    return wrapper


class ErrorCode:
    """
    Centralized error codes for consistent error handling.
    """

    # Authentication errors
    AUTHENTICATION_FAILED = "authentication_failed"
    INVALID_TOKEN = "invalid_token"
    TOKEN_EXPIRED = "token_expired"
    INVALID_CREDENTIALS = "invalid_credentials"
    ACCOUNT_LOCKED = "account_locked"
    EMAIL_NOT_VERIFIED = "email_not_verified"

    # Authorization errors
    PERMISSION_DENIED = "permission_denied"
    INSUFFICIENT_PERMISSIONS = "insufficient_permissions"

    # Validation errors
    VALIDATION_ERROR = "validation_error"
    INVALID_INPUT = "invalid_input"
    MISSING_REQUIRED_FIELD = "missing_required_field"

    # Resource errors
    NOT_FOUND = "not_found"
    DUPLICATE_RESOURCE = "duplicate_resource"
    RESOURCE_IN_USE = "resource_in_use"

    # Business logic errors
    BUSINESS_LOGIC_ERROR = "business_logic_error"
    INVALID_OPERATION = "invalid_operation"
    INSUFFICIENT_FUNDS = "insufficient_funds"

    # System errors
    INTERNAL_ERROR = "internal_error"
    DATABASE_ERROR = "database_error"
    EXTERNAL_SERVICE_ERROR = "external_service_error"
    SERVICE_UNAVAILABLE = "service_unavailable"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"


class ErrorMessage:
    """
    Centralized error messages for consistent messaging.
    """

    # Authentication messages
    AUTHENTICATION_FAILED = "Authentication failed"
    INVALID_TOKEN = "Invalid or expired token"
    TOKEN_EXPIRED = "Token has expired"
    INVALID_CREDENTIALS = "Invalid username or password"
    ACCOUNT_LOCKED = "Account is locked due to too many failed login attempts"
    EMAIL_NOT_VERIFIED = "Email address not verified"

    # Authorization messages
    PERMISSION_DENIED = "You don't have permission to perform this action"
    INSUFFICIENT_PERMISSIONS = "Insufficient permissions for this operation"

    # Validation messages
    VALIDATION_ERROR = "Validation failed"
    INVALID_INPUT = "Invalid input provided"
    MISSING_REQUIRED_FIELD = "Required field is missing"

    # Resource messages
    NOT_FOUND = "Resource not found"
    DUPLICATE_RESOURCE = "Resource already exists"
    RESOURCE_IN_USE = "Resource is currently in use and cannot be deleted"

    # Business logic messages
    BUSINESS_LOGIC_ERROR = "Business logic error"
    INVALID_OPERATION = "Operation not valid in current context"

    # System messages
    INTERNAL_ERROR = "Internal server error"
    DATABASE_ERROR = "Database operation failed"
    EXTERNAL_SERVICE_ERROR = "External service error"
    SERVICE_UNAVAILABLE = "Service temporarily unavailable"
    RATE_LIMIT_EXCEEDED = "Rate limit exceeded"
