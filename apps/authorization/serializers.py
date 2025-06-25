from rest_framework import serializers
from apps.authorization.models import Role, Permission, UserRole


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name", "description", "created_at", "updated_at"]


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ["id", "name", "codename", "created_at", "updated_at"]


class UserRoleSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    role = serializers.StringRelatedField()

    class Meta:
        model = UserRole
        fields = ["id", "user", "role", "created_at", "updated_at"]


class RoleAssignmentSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    role_id = serializers.UUIDField()


class PermissionAssignmentSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    permission_id = serializers.UUIDField()
