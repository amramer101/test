from django.core.cache import cache
from django.http import JsonResponse
from django.utils.timezone import now
from django.conf import settings
import hashlib


# This middleware is now deprecated in favor of DRF's built-in throttling.
# To avoid conflicts, disable this middleware if DRF throttling is enabled in settings.
# If you want to keep this middleware, ensure it checks for DRF throttle headers and does not double-limit requests.
# To fully disable, comment out or remove 'middleware.rate_limiting.RateLimitingMiddleware' from MIDDLEWARE in settings.
class RateLimitingMiddleware:
    """
    Middleware to enforce rate limiting on API endpoints.
    Deprecated: Prefer DRF's built-in throttling system.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit = getattr(
            settings, "RATE_LIMIT", 100
        )  # Default: 100 requests per minute
        self.rate_limit_window = getattr(
            settings, "RATE_LIMIT_WINDOW", 60
        )  # Default: 60 seconds

    def __call__(self, request):
        # If DRF throttle headers are present, skip this middleware
        if (
            hasattr(request, "META")
            and (
                "HTTP_X_RATELIMIT_LIMIT" in request.META
                or "HTTP_X_RATELIMIT_REMAINING" in request.META
            )
        ):
            return self.get_response(request)
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            identifier = str(user.id)
        else:
            identifier = self._get_client_ip(request)
        endpoint = request.path
        cache_key = self._generate_cache_key(identifier, endpoint)

        request_count = cache.get(cache_key, 0)
        if request_count >= self.rate_limit:
            return JsonResponse(
                {"error": "Rate limit exceeded. Try again later."}, status=429
            )

        cache.set(cache_key, request_count + 1, timeout=self.rate_limit_window)

        response = self.get_response(request)
        response["X-RateLimit-Limit"] = str(self.rate_limit)
        response["X-RateLimit-Remaining"] = str(
            max(0, self.rate_limit - request_count - 1)
        )
        return response

    def _get_client_ip(self, request):
        """
        Extracts the client IP address from the request.
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR")

    def _generate_cache_key(self, identifier, endpoint):
        """
        Generates a unique cache key for rate limiting based on client IP and endpoint.
        """
        key = f"{identifier}:{endpoint}"
        return hashlib.sha256(key.encode()).hexdigest()
