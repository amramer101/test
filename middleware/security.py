from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.http import HttpResponseForbidden


class SecurityMiddleware(MiddlewareMixin):
    """
    Middleware to enhance security by adding headers and validating requests.
    Coordinates with Django's built-in SecurityMiddleware to avoid duplicate headers.
    """

    def process_request(self, request):
        # Validate IP address if IP filtering is enabled
        if hasattr(settings, "ALLOWED_IPS") and settings.ALLOWED_IPS:
            client_ip = self._get_client_ip(request)
            if client_ip not in settings.ALLOWED_IPS:
                return HttpResponseForbidden("Access denied: Unauthorized IP address.")

    def process_response(self, request, response):
        # Avoid duplicating headers if Django's SecurityMiddleware is present
        if hasattr(response, "_security_middleware_applied"):
            return response
        # Only set security headers if not already set by Django's SecurityMiddleware
        if not response.has_header("Strict-Transport-Security"):
            response["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        if not response.has_header("X-Content-Type-Options"):
            response["X-Content-Type-Options"] = "nosniff"
        if not response.has_header("X-Frame-Options"):
            response["X-Frame-Options"] = "DENY"
        if not response.has_header("Referrer-Policy"):
            response["Referrer-Policy"] = "no-referrer"
        # Allow inline scripts/styles and local static assets for API docs endpoints and their static sidecar assets
        api_docs_paths = [
            "/api/docs",
            "/api/redoc",
            "/api/docs/sidecar/",
            "/api/redoc/sidecar/",
        ]
        if any(request.path.startswith(path) for path in api_docs_paths):
            response["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "img-src 'self' data: https:; "
                "font-src 'self' data: https://fonts.gstatic.com; "
                "connect-src 'self'; "
            )
        else:
            response["Content-Security-Policy"] = (
                "default-src 'self'; script-src 'self'; style-src 'self';"
            )
        response._security_middleware_applied = True
        return response

    def _get_client_ip(self, request):
        """
        Extracts the client's IP address from the request.
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
