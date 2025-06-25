from uuid import uuid4
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from apps.authentication.models import User, PasswordResetToken, EmailVerificationToken
from infrastructure.email import EmailService


class AuthenticationService:
    """
    Service layer for authentication-related use cases.
    Uses Django ORM directly and integrates with email infrastructure.
    """

    def __init__(self):
        self.UserModel = get_user_model()
        self.email_service = EmailService()

    def register_user(self, username: str, email: str, password: str) -> User:
        if self.UserModel.objects.filter(email=email).exists():
            raise ValueError("A user with this email already exists.")
        user = self.UserModel.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            is_active=False,
            is_email_verified=False,
        )
        verification_token = self._generate_email_verification_token(user)
        try:
            self.email_service.send_verification_email(email, verification_token.token)
        except Exception as e:
            # Optionally handle email sending errors
            pass
        return user

    def login_user(self, email: str, password: str) -> User:
        try:
            user = self.UserModel.objects.get(email=email)
        except self.UserModel.DoesNotExist:
            raise ValueError("Invalid credentials")
        if not check_password(password, user.password):
            raise ValueError("Invalid credentials")
        if not user.is_active:
            raise ValueError("User account is not active")
        return user  # Token generation handled by SimpleJWT view

    def reset_password(self, email: str) -> None:
        try:
            user = self.UserModel.objects.get(email=email)
        except self.UserModel.DoesNotExist:
            raise ValueError("User not found")
        reset_token = self._generate_password_reset_token(user)
        try:
            self.email_service.send_password_reset_email(email, reset_token.token)
        except Exception as e:
            # Optionally handle email sending errors
            pass

    def verify_email(self, user_id: str, token: str) -> bool:
        try:
            user = self.UserModel.objects.get(id=user_id)
        except self.UserModel.DoesNotExist:
            return False
        verification_token = self._get_email_verification_token(user)
        if (
            verification_token
            and verification_token.token == token
            and verification_token.is_valid()
        ):
            user.is_active = True
            user.is_email_verified = True
            user.save()
            verification_token.is_used = True
            verification_token.save()
            return True
        return False

    def change_password(self, user: User, new_password: str) -> None:
        user.password = make_password(new_password)
        user.save()

    def _generate_password_reset_token(self, user: User) -> PasswordResetToken:
        token = PasswordResetToken.objects.create(
            user=user,
            token=str(uuid4()),
            expires_at=timezone.now() + timedelta(hours=1),
        )
        return token

    def _generate_email_verification_token(self, user: User) -> EmailVerificationToken:
        token = EmailVerificationToken.objects.create(
            user=user, token=str(uuid4()), expires_at=timezone.now() + timedelta(days=1)
        )
        return token

    def _get_email_verification_token(self, user: User) -> EmailVerificationToken:
        try:
            return EmailVerificationToken.objects.filter(
                user=user, is_used=False, expires_at__gt=timezone.now()
            ).latest("created_at")
        except EmailVerificationToken.DoesNotExist:
            return None
