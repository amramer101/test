from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model

from ..application.serializers import UserRegistrationSerializer, UserLoginSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenBlacklistView
from apps.users.serializers import UserProfileSerializer
from apps.users.models import UserProfile

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                return Response(
                    {"id": str(user.id), "email": user.email},
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer


class LogoutView(TokenBlacklistView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # JWT Blacklisting (if enabled)
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "Refresh token required for logout."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            # Use SimpleJWT's token blacklisting
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"detail": "Successfully logged out."}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"detail": f"Logout failed: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class PasswordResetView(APIView):
    permission_classes = [AllowAny]
    serializer_class = None

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response(
                {"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        service = AuthenticationService()
        try:
            service.reset_password(email)
            return Response(
                {"detail": "Password reset email sent."}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get(self, request):
        user = request.user
        try:
            profile = getattr(user, "profile", None)
            user_data = {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "is_email_verified": getattr(user, "is_email_verified", False),
            }
            if profile:
                user_data["profile"] = UserProfileSerializer(profile).data
            else:
                user_data["profile"] = None
            return Response(user_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"detail": f"Could not retrieve profile: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
