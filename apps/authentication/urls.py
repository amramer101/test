from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)

app_name = "authentication"

urlpatterns = [
    # JWT Token endpoints
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", TokenBlacklistView.as_view(), name="token_blacklist"),
    # Placeholder for future authentication endpoints
    # path('register/', views.RegisterView.as_view(), name='register'),
    # path('password-reset/', views.PasswordResetView.as_view(), name='password_reset'),
    # path('verify-email/', views.EmailVerificationView.as_view(), name='verify_email'),
]
