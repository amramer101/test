from rest_framework import permissions
from rest_framework.permissions import BasePermission
from django.contrib.auth.models import AnonymousUser
from guardian.shortcuts import get_objects_for_user
from django.core.exceptions import ObjectDoesNotExist
from apps.authorization.models import UserRole, Role, Permission


class IsOwnerOrReadOnly(BasePermission):
    """
    Permission that only allows owners of an object to edit it.
    Assumes the model instance has an 'owner' attribute.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.owner == request.user


class IsCreatorOrReadOnly(BasePermission):
    """
    Permission that only allows creators of an object to edit it.
    Assumes the model instance has a 'created_by' attribute.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return getattr(obj, "created_by", None) == request.user


class IsAdminOrReadOnly(BasePermission):
    """
    Permission that only allows admin users to modify objects.
    All users can read.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user and request.user.is_staff


class IsOwnerOrAdmin(BasePermission):
    """
    Permission that allows owners and admin users to access objects.
    """

    def has_object_permission(self, request, view, obj):
        return request.user and (request.user.is_staff or obj.owner == request.user)


class RoleBasedPermission(BasePermission):
    """
    Permission class that checks if user has required role.
    Usage: Set required_roles in view class.
    """

    def has_permission(self, request, view):
        if isinstance(request.user, AnonymousUser):
            return False

        required_roles = getattr(view, "required_roles", [])
        if not required_roles:
            return True

        user_roles = UserRole.objects.filter(user=request.user).values_list(
            "role__name", flat=True
        )
        return any(role in user_roles for role in required_roles)


class PermissionRequired(BasePermission):
    """
    Permission class that checks if user has required permissions.
    Usage: Set required_permissions in view class or pass as constructor argument.
    """

    def __init__(self, required_permissions=None):
        # Accept required_permissions as a constructor argument for flexibility
        self.required_permissions = required_permissions

    def has_permission(self, request, view):
        if isinstance(request.user, AnonymousUser):
            return False

        # Prefer instance variable, fallback to view attribute, then class attribute
        required_permissions = (
            self.required_permissions
            if self.required_permissions is not None
            else getattr(view, "required_permissions", [])
        )
        if not required_permissions:
            return True

        user_permissions = Permission.objects.filter(
            userrole__user=request.user
        ).values_list("codename", flat=True)
        return any(perm in user_permissions for perm in required_permissions)


class ObjectPermissionMixin(BasePermission):
    """
    Permission class that uses django-guardian for object-level permissions.
    """

    def has_permission(self, request, view):
        if isinstance(request.user, AnonymousUser):
            return False
        return True

    def has_object_permission(self, request, view, obj):
        required_perm = getattr(view, "required_permission", None)
        if not required_perm:
            return True

        return request.user.has_perm(required_perm, obj)


class DynamicPermission(BasePermission):
    """
    Permission class that allows dynamic permission checking based on view action.
    """

    def has_permission(self, request, view):
        if isinstance(request.user, AnonymousUser):
            action_permissions = getattr(view, "anonymous_permissions", {})
        else:
            action_permissions = getattr(view, "action_permissions", {})

        current_action = getattr(view, "action", None)
        if current_action and current_action in action_permissions:
            permission_classes = action_permissions[current_action]
            for permission_class in permission_classes:
                permission = permission_class()
                if not permission.has_permission(request, view):
                    return False

        return True


class APIKeyPermission(BasePermission):
    """
    Permission class that checks for valid API key in headers.
    """

    def has_permission(self, request, view):
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            return False

        # Add your API key validation logic here
        # This is a basic example - in production, store keys in database
        valid_keys = getattr(view, "valid_api_keys", [])
        return api_key in valid_keys


class ThrottledPermission(BasePermission):
    """
    Permission class that works with DRF throttling.
    Can be extended to add custom throttling logic.
    """

    def has_permission(self, request, view):
        if isinstance(request.user, AnonymousUser):
            return getattr(view, "allow_anonymous", False)

        return True


class ResourcePermission(BasePermission):
    """
    Permission class for resource-based access control.
    Checks if user has permission to access specific resource types.
    """

    def has_permission(self, request, view):
        if isinstance(request.user, AnonymousUser):
            return False

        resource_type = getattr(view, "resource_type", None)
        if not resource_type:
            return True

        method_permission_map = {
            "GET": f"view_{resource_type}",
            "POST": f"add_{resource_type}",
            "PUT": f"change_{resource_type}",
            "PATCH": f"change_{resource_type}",
            "DELETE": f"delete_{resource_type}",
        }

        required_permission = method_permission_map.get(request.method)
        if not required_permission:
            return False

        return request.user.has_perm(required_permission)


class ConditionalPermission(BasePermission):
    """
    Permission class that applies different permissions based on conditions.
    """

    def has_permission(self, request, view):
        permission_conditions = getattr(view, "permission_conditions", {})

        for condition, permission_classes in permission_conditions.items():
            if self._evaluate_condition(condition, request, view):
                for permission_class in permission_classes:
                    permission = permission_class()
                    if not permission.has_permission(request, view):
                        return False
                return True

        return True

    def _evaluate_condition(self, condition, request, view):
        """
        Evaluate permission condition. Override this method to add custom conditions.
        """
        if condition == "is_authenticated":
            return request.user.is_authenticated
        elif condition == "is_staff":
            return request.user.is_staff
        elif condition == "is_superuser":
            return request.user.is_superuser

        return False


class SoftDeletePermission(BasePermission):
    """
    Permission class that respects soft delete status.
    Prevents access to soft-deleted objects unless user has special permission.
    """

    def has_object_permission(self, request, view, obj):
        if not hasattr(obj, "is_deleted"):
            return True

        if obj.is_deleted:
            return request.user.has_perm("view_deleted_objects")

        return True


class TimeBasedPermission(BasePermission):
    """
    Permission class that restricts access based on time conditions.
    """

    def has_permission(self, request, view):
        from django.utils import timezone

        time_restrictions = getattr(view, "time_restrictions", {})
        if not time_restrictions:
            return True

        current_time = timezone.now()

        if "start_time" in time_restrictions:
            if current_time < time_restrictions["start_time"]:
                return False

        if "end_time" in time_restrictions:
            if current_time > time_restrictions["end_time"]:
                return False

        return True


class IPBasedPermission(BasePermission):
    """
    Permission class that restricts access based on IP address.
    """

    def has_permission(self, request, view):
        allowed_ips = getattr(view, "allowed_ips", [])
        blocked_ips = getattr(view, "blocked_ips", [])

        client_ip = self._get_client_ip(request)

        if blocked_ips and client_ip in blocked_ips:
            return False

        if allowed_ips and client_ip not in allowed_ips:
            return False

        return True

    def _get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class FieldLevelPermission(BasePermission):
    """
    Permission class for field-level access control.
    Can be used with custom serializers to control field visibility.
    """

    def has_permission(self, request, view):
        return True

    def can_access_field(self, user, field_name, obj=None):
        """
        Check if user can access specific field.
        Override this method to implement field-level permissions.
        """
        if user.is_superuser:
            return True

        # Default implementation - can be extended
        restricted_fields = getattr(self, "restricted_fields", {})
        if field_name in restricted_fields:
            required_permission = restricted_fields[field_name]
            return (
                user.has_perm(required_permission, obj)
                if obj
                else user.has_perm(required_permission)
            )

        return True


class IsOwner(permissions.BasePermission):
    """Allows access only to the owner of the object."""

    def has_object_permission(self, request, view, obj):
        return hasattr(obj, "owner") and obj.owner == request.user


def permission_factory(user_field="user"):
    class IsUserItself(permissions.BasePermission):
        def has_object_permission(self, request, view, obj):
            return getattr(obj, user_field, None) == request.user

    return IsUserItself


class DynamicPermissionRequired(BasePermission):
    """
    Permission class that accepts a permission string as a constructor argument and checks it dynamically.
    """

    def __init__(self, required_permission):
        self.required_permission = required_permission

    def has_permission(self, request, view):
        if isinstance(request.user, AnonymousUser):
            return False
        if not self.required_permission:
            return True
        user_permissions = Permission.objects.filter(
            userrole__user=request.user
        ).values_list("codename", flat=True)
        return self.required_permission in user_permissions
