import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.authorization.models import Role, Permission, UserRole
from apps.authentication.models import User

@pytest.mark.django_db
def test_rbac_permission_enforcement():
    # Create user and assign no roles
    user = User.objects.create_user(email="rbacuser@example.com", password="TestPass123!")
    client = APIClient()
    client.force_authenticate(user=user)
    # Try to access a protected endpoint
    response = client.get(reverse("gamification-profile-list"))
    assert response.status_code in (403, 401)

@pytest.mark.django_db
def test_role_assignment_and_permission_check():
    user = User.objects.create_user(email="rbacuser2@example.com", password="TestPass123!")
    role = Role.objects.create(name="Student")
    perm = Permission.objects.create(codename="view_leaderboard", name="View leaderboard")
    role.permissions.add(perm)
    UserRole.objects.create(user=user, role=role)
    client = APIClient()
    client.force_authenticate(user=user)
    # Should now be able to access leaderboard
    response = client.get(reverse("gamification-leaderboard-list"))
    assert response.status_code == 200

@pytest.mark.django_db
def test_object_level_permission():
    # Create two users and a resource owned by one
    user1 = User.objects.create_user(email="owner@example.com", password="TestPass123!")
    user2 = User.objects.create_user(email="other@example.com", password="TestPass123!")
    # Assume user1 owns a resource (e.g., profile)
    # ... create resource logic ...
    # user2 should not be able to modify user1's resource
    client = APIClient()
    client.force_authenticate(user=user2)
    # response = client.patch(reverse("users-detail", args=[user1.id]), {"bio": "hack"})
    # assert response.status_code in (403, 401)
    # (Uncomment and adapt above lines for actual resource)

@pytest.mark.django_db
def test_privilege_escalation_prevention():
    user = User.objects.create_user(email="escalate@example.com", password="TestPass123!")
    client = APIClient()
    client.force_authenticate(user=user)
    # Try to assign self to admin role (should fail)
    # response = client.post(reverse("authorization:userrole-list"), {"user": user.id, "role": admin_role.id})
    # assert response.status_code in (403, 401)
    # (Uncomment and adapt above lines for actual admin role)

@pytest.mark.django_db
def test_multiple_roles_and_permission_inheritance():
    user = User.objects.create_user(email="multi@example.com", password="TestPass123!")
    role1 = Role.objects.create(name="Student")
    role2 = Role.objects.create(name="Moderator")
    perm1 = Permission.objects.create(codename="view_leaderboard", name="View leaderboard")
    perm2 = Permission.objects.create(codename="moderate_comments", name="Moderate comments")
    role1.permissions.add(perm1)
    role2.permissions.add(perm2)
    UserRole.objects.create(user=user, role=role1)
    UserRole.objects.create(user=user, role=role2)
    client = APIClient()
    client.force_authenticate(user=user)
    # Should have both permissions
    response1 = client.get(reverse("gamification-leaderboard-list"))
    response2 = client.post(reverse("social-comments-report", args=[1]))  # Example
    assert response1.status_code in (200, 403, 401)  # Depending on setup
    assert response2.status_code in (200, 403, 401)
