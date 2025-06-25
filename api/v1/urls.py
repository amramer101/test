from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

app_name = "v1"

router = DefaultRouter()
# router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("apps.authentication.api.urls")),
    path("auth/jwt/login/", TokenObtainPairView.as_view(), name="jwt-login"),
    path("auth/jwt/refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),
    path("users/", include(("apps.users.urls", "users"), namespace="users")),
    path(
        "authorization/",
        include(
            ("apps.authorization.urls", "authorization"), namespace="authorization"
        ),
    ),
    path("gamification/", include("apps.gamification.urls")),
    path("courses/", include(("apps.courses.urls", "courses"), namespace="courses")),
    path("shop/", include(("apps.shop.urls", "shop"), namespace="shop")),
    path("social/", include(("apps.social.urls", "social"), namespace="social")),
]
