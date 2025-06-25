import pytest
from apps.authorization.models import Role, Permission, UserRole
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


@pytest.mark.django_db
def test_role_creation():
    role = Role.objects.create(name="Admin", description="Administrator role")
    assert role.name == "Admin"
    assert str(role) == "Admin"


@pytest.mark.django_db
def test_permission_creation():
    perm = Permission.objects.create(
        name="edit_course", description="Edit course permission"
    )
    assert perm.name == "edit_course"
    assert str(perm) == "edit_course"


@pytest.mark.django_db
def test_userrole_unique_constraint():
    user = User.objects.create_user(
        username="rbacuser", email="rbac@example.com", password="pass"
    )
    role = Role.objects.create(name="Editor")
    ur1 = UserRole.objects.create(user=user, role=role)
    with pytest.raises(IntegrityError):
        UserRole.objects.create(user=user, role=role)


@pytest.mark.django_db
def test_soft_delete_role():
    role = Role.objects.create(name="SoftDeleteRole")
    role.is_deleted = True
    role.save()
    assert Role.objects.filter(is_deleted=True).count() == 1
