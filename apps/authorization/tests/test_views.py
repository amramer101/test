import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.authorization.models import Role, Permission, UserRole

User = get_user_model()


@pytest.mark.django_db
def test_role_crud():
    client = APIClient()
    user = User.objects.create_user(
        username="admin", email="admin@example.com", password="pass"
    )
    client.force_authenticate(user=user)
    url = reverse("role-list")
    data = {"name": "Instructor", "description": "Can instruct courses"}
    response = client.post(url, data)
    assert response.status_code == 201
    role_id = response.data["id"]
    get_response = client.get(reverse("role-detail", args=[role_id]))
    assert get_response.status_code == 200
    patch_response = client.patch(
        reverse("role-detail", args=[role_id]),
        {"description": "Updated"},
        format="json",
    )
    assert patch_response.status_code == 200
    del_response = client.delete(reverse("role-detail", args=[role_id]))
    assert del_response.status_code in (204, 200)


@pytest.mark.django_db
def test_permission_crud():
    client = APIClient()
    user = User.objects.create_user(
        username="permuser", email="perm@example.com", password="pass"
    )
    client.force_authenticate(user=user)
    url = reverse("permission-list")
    data = {"name": "view_course", "description": "Can view courses"}
    response = client.post(url, data)
    assert response.status_code == 201
    perm_id = response.data["id"]
    get_response = client.get(reverse("permission-detail", args=[perm_id]))
    assert get_response.status_code == 200


@pytest.mark.django_db
def test_userrole_assignment():
    client = APIClient()
    user = User.objects.create_user(
        username="assignuser", email="assign@example.com", password="pass"
    )
    role = Role.objects.create(name="Student")
    client.force_authenticate(user=user)
    url = reverse("userrole-list")
    data = {"user": user.id, "role": role.id}
    response = client.post(url, data)
    assert response.status_code == 201
    assert UserRole.objects.filter(user=user, role=role).exists()
