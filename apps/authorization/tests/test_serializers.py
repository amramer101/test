import pytest
from apps.authorization.serializers import (
    RoleSerializer,
    PermissionSerializer,
    UserRoleSerializer,
    RoleAssignmentSerializer,
    PermissionAssignmentSerializer,
)
from apps.authorization.models import Role, Permission, UserRole
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_role_serializer():
    role = Role.objects.create(name="TestRole", description="desc")
    serializer = RoleSerializer(role)
    assert serializer.data["name"] == "TestRole"


@pytest.mark.django_db
def test_permission_serializer():
    perm = Permission.objects.create(name="perm", description="desc")
    serializer = PermissionSerializer(perm)
    assert serializer.data["name"] == "perm"


@pytest.mark.django_db
def test_userrole_serializer():
    user = User.objects.create_user(
        username="seruser", email="seruser@example.com", password="pass"
    )
    role = Role.objects.create(name="Role")
    ur = UserRole.objects.create(user=user, role=role)
    serializer = UserRoleSerializer(ur)
    assert serializer.data["user"] == user.id
    assert serializer.data["role"] == role.id


@pytest.mark.django_db
def test_role_assignment_serializer():
    user = User.objects.create_user(
        username="assign", email="assign@example.com", password="pass"
    )
    role = Role.objects.create(name="Role")
    data = {"user": user.id, "role": role.id}
    serializer = RoleAssignmentSerializer(data=data)
    assert serializer.is_valid(), serializer.errors


@pytest.mark.django_db
def test_permission_assignment_serializer():
    user = User.objects.create_user(
        username="assign2", email="assign2@example.com", password="pass"
    )
    perm = Permission.objects.create(name="perm2")
    data = {"user": user.id, "permission": perm.id}
    serializer = PermissionAssignmentSerializer(data=data)
    assert serializer.is_valid(), serializer.errors
