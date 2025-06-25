from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.authorization.views import RoleViewSet, PermissionViewSet, UserRoleViewSet

router = DefaultRouter()
router.register(r"roles", RoleViewSet, basename="role")
router.register(r"permissions", PermissionViewSet, basename="permission")
router.register(r"user-roles", UserRoleViewSet, basename="userrole")

app_name = "authorization"

urlpatterns = [
    path("", include(router.urls)),
]
