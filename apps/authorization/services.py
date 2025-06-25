from apps.authorization.models import Role, Permission, UserRole
from apps.authentication.models import User


class AuthorizationService:
    @staticmethod
    def assign_role_to_user(user: User, role: Role) -> UserRole:
        user_role, created = UserRole.objects.get_or_create(user=user, role=role)
        return user_role

    @staticmethod
    def remove_role_from_user(user: User, role: Role) -> None:
        UserRole.objects.filter(user=user, role=role).delete()

    @staticmethod
    def check_user_permission(user: User, permission_codename: str) -> bool:
        user_roles = UserRole.objects.filter(user=user).select_related("role")
        permissions = Permission.objects.filter(
            codename=permission_codename,
            role__in=[user_role.role for user_role in user_roles],
        )
        return permissions.exists()

    @staticmethod
    def create_role(name: str, description: str = "") -> Role:
        role = Role.objects.create(name=name, description=description)
        return role

    @staticmethod
    def create_permission(name: str, codename: str) -> Permission:
        permission = Permission.objects.create(name=name, codename=codename)
        return permission

    @staticmethod
    def assign_permission_to_role(role: Role, permission: Permission) -> None:
        role.permissions.add(permission)

    @staticmethod
    def remove_permission_from_role(role: Role, permission: Permission) -> None:
        role.permissions.remove(permission)
