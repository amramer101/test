from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.users.views import UserViewSet

router = DefaultRouter()
router.register(r"", UserViewSet, basename="user")

app_name = "users"

urlpatterns = [
    path("", include(router.urls)),
]
