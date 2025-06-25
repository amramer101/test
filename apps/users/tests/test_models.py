import pytest
from django.contrib.auth import get_user_model
from apps.users.models import UserProfile
from django.db import IntegrityError

User = get_user_model()


@pytest.mark.django_db
def test_user_profile_creation():
    user = User.objects.create_user(
        username="testuser", email="test@example.com", password="pass"
    )
    profile = UserProfile.objects.create(user=user, bio="Test bio")
    assert profile.user == user
    assert profile.bio == "Test bio"
    assert str(profile) == f"Profile of {user.username}"


@pytest.mark.django_db
def test_user_profile_onetoone():
    user = User.objects.create_user(
        username="uniqueuser", email="unique@example.com", password="pass"
    )
    UserProfile.objects.create(user=user)
    with pytest.raises(IntegrityError):
        UserProfile.objects.create(user=user)


@pytest.mark.django_db
def test_user_profile_cascade_delete():
    user = User.objects.create_user(
        username="deluser", email="del@example.com", password="pass"
    )
    profile = UserProfile.objects.create(user=user)
    user.delete()
    assert UserProfile.objects.filter(pk=profile.pk).count() == 0
