import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.users.models import UserProfile

User = get_user_model()


@pytest.mark.django_db
def test_user_registration():
    client = APIClient()
    url = reverse("users-register")
    data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "strongpassword123",
    }
    response = client.post(url, data)
    assert response.status_code == 201
    assert User.objects.filter(username="newuser").exists()


@pytest.mark.django_db
def test_user_login():
    client = APIClient()
    user = User.objects.create_user(
        username="loginuser", email="login@example.com", password="testpass"
    )
    url = reverse("users-login")
    data = {"username": "loginuser", "password": "testpass"}
    response = client.post(url, data)
    assert response.status_code == 200
    assert "token" in response.data


@pytest.mark.django_db
def test_user_profile_retrieve():
    client = APIClient()
    user = User.objects.create_user(
        username="profileuser", email="profile@example.com", password="testpass"
    )
    profile = UserProfile.objects.create(user=user, bio="Bio")
    client.force_authenticate(user=user)
    url = reverse("users-profile")
    response = client.get(url)
    assert response.status_code == 200
    assert response.data["bio"] == "Bio"
