import pytest
from apps.users.serializers import (
    UserSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
)
from django.contrib.auth import get_user_model
from apps.users.models import UserProfile

User = get_user_model()


@pytest.mark.django_db
def test_user_serializer():
    user = User.objects.create_user(
        username="seruser", email="ser@example.com", password="pass"
    )
    serializer = UserSerializer(user)
    assert serializer.data["username"] == "seruser"
    assert serializer.data["email"] == "ser@example.com"


@pytest.mark.django_db
def test_user_profile_serializer():
    user = User.objects.create_user(
        username="profileuser", email="profile@example.com", password="pass"
    )
    profile = UserProfile.objects.create(user=user, bio="Bio")
    serializer = UserProfileSerializer(profile)
    assert serializer.data["bio"] == "Bio"


@pytest.mark.django_db
def test_user_registration_serializer():
    data = {
        "username": "reguser",
        "email": "reg@example.com",
        "password": "strongpass123",
    }
    serializer = UserRegistrationSerializer(data=data)
    assert serializer.is_valid(), serializer.errors
    user = serializer.save()
    assert user.username == "reguser"
    assert user.email == "reg@example.com"


@pytest.mark.django_db
def test_user_login_serializer():
    user = User.objects.create_user(
        username="loginser", email="loginser@example.com", password="pass"
    )
    data = {"username": "loginser", "password": "pass"}
    serializer = UserLoginSerializer(data=data)
    assert serializer.is_valid(), serializer.errors
