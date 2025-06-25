import logging
import time
from django.utils.deprecation import MiddlewareMixin
from django.utils.timezone import now
from apps.shared.models import AuditLog

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log incoming requests, outgoing responses, exceptions, and performance metrics.
    Uses the AuditLog model for persistent audit logging.
    """

    def process_request(self, request):
        """
        Logs the details of the incoming request and creates an AuditLog entry.
        Stores the start time for performance metrics.
        """
        request._logging_start_time = time.monotonic()
        user = (
            request.user
            if hasattr(request, "user") and request.user.is_authenticated
            else None
        )
        ip_address = self._get_client_ip(request)
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        logger.info(
            f"[Request] {request.method} {request.path} | User={user or 'Anonymous'} | IP={ip_address}"
        )
        try:
            AuditLog.log_action(
                user=user,
                action="VIEW",
                resource_type="API_REQUEST",
                resource_id=None,
                resource_repr=f"{request.method} {request.path}",
                ip_address=ip_address,
                user_agent=user_agent,
            )
        except Exception as e:
            logger.error(f"Failed to create AuditLog for request: {e}", exc_info=True)

    def process_response(self, request, response):
        """
        Logs the details of the outgoing response and creates an AuditLog entry.
        Records performance metrics (duration).
        """
        user = (
            request.user
            if hasattr(request, "user") and request.user.is_authenticated
            else None
        )
        ip_address = self._get_client_ip(request)
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        duration_ms = None
        if hasattr(request, "_logging_start_time"):
            duration_ms = int((time.monotonic() - request._logging_start_time) * 1000)
        logger.info(
            f"[Response] {request.method} {request.path} | Status={response.status_code} | "
            f"User={user or 'Anonymous'} | IP={ip_address} | Duration={duration_ms}ms"
        )
        try:
            AuditLog.log_action(
                user=user,
                action="VIEW",
                resource_type="API_RESPONSE",
                resource_id=None,
                resource_repr=f"{request.method} {request.path}",
                ip_address=ip_address,
                user_agent=user_agent,
            )
        except Exception as e:
            logger.error(f"Failed to create AuditLog for response: {e}", exc_info=True)
        return response

    def process_exception(self, request, exception):
        """
        Logs any exceptions that occur during request processing and creates an AuditLog entry.
        """
        user = (
            request.user
            if hasattr(request, "user") and request.user.is_authenticated
            else None
        )
        ip_address = self._get_client_ip(request)
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        logger.error(
            f"[Exception] {request.method} {request.path} | User={user or 'Anonymous'} | "
            f"IP={ip_address} | Error={str(exception)}"
        )
        try:
            AuditLog.log_action(
                user=user,
                action="EXCEPTION",
                resource_type="API_EXCEPTION",
                resource_id=None,
                resource_repr=f"{request.method} {request.path}",
                ip_address=ip_address,
                user_agent=user_agent,
            )
        except Exception as e:
            logger.error(f"Failed to create AuditLog for exception: {e}", exc_info=True)

    def _get_client_ip(self, request):
        """
        Retrieves the client's IP address from the request, stripping any port if present.
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR")
        # Remove port if present (e.g., '1.2.3.4:56789')
        if ip and ":" in ip:
            ip = ip.split(":")[0]
        return ip
