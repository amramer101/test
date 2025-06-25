import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.authentication.models import User

@pytest.mark.django_db
def test_token_blacklisting():
    user = User.objects.create_user(email="jwtuser@example.com", password="TestPass123!")
    client = APIClient()
    # Obtain token
    response = client.post(reverse("login"), {"email": user.email, "password": "TestPass123!"})
    assert response.status_code == 200
    refresh = response.data["refresh"]
    # Logout (blacklist refresh token)
    response = client.post(reverse("logout"), {"refresh": refresh})
    assert response.status_code == 200
    # Try to use blacklisted refresh token
    response = client.post(reverse("token_refresh"), {"refresh": refresh})
    assert response.status_code == 401
    assert "token" in str(response.data).lower()

@pytest.mark.django_db
def test_token_expiration_and_refresh():
    user = User.objects.create_user(email="jwtuser2@example.com", password="TestPass123!")
    client = APIClient()
    response = client.post(reverse("login"), {"email": user.email, "password": "TestPass123!"})
    assert response.status_code == 200
    refresh = response.data["refresh"]
    access = response.data["access"]
    # Use refresh to get new access
    response = client.post(reverse("token_refresh"), {"refresh": refresh})
    assert response.status_code == 200
    assert "access" in response.data

@pytest.mark.django_db
def test_authentication_bypass_attempt():
    client = APIClient()
    # Try to access protected endpoint without token
    response = client.get(reverse("profile"))
    assert response.status_code == 401
    # Try with invalid token
    client.credentials(HTTP_AUTHORIZATION="Bearer invalidtoken")
    response = client.get(reverse("profile"))
    assert response.status_code == 401

@pytest.mark.django_db
def test_token_reuse_after_logout():
    user = User.objects.create_user(email="jwtuser3@example.com", password="TestPass123!")
    client = APIClient()
    response = client.post(reverse("login"), {"email": user.email, "password": "TestPass123!"})
    refresh = response.data["refresh"]
    # Logout
    client.post(reverse("logout"), {"refresh": refresh})
    # Try to use refresh again
    response = client.post(reverse("token_refresh"), {"refresh": refresh})
    assert response.status_code == 401

@pytest.mark.django_db
def test_malformed_token_handling():
    client = APIClient()
    response = client.post(reverse("token_refresh"), {"refresh": "notatoken"})
    assert response.status_code == 401
    assert "token" in str(response.data).lower()
