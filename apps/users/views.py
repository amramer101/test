from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model, authenticate
from django.db.models import Q
from apps.users.models import UserProfile
from apps.users.serializers import (
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
)
from rest_framework.parsers import MultiPartParser, FormParser
from apps.shared.permissions import RoleBasedPermission, PermissionRequired, IsOwnerOrReadOnly

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user profiles and user-related actions.
    """

    queryset = UserProfile.objects.select_related("user").all()
    serializer_class = UserProfileSerializer
    permission_classes = [RoleBasedPermission, IsOwnerOrReadOnly]
    permission_required_map = {
        "update_profile": ["update_profile"],
        "update_preferences": ["update_preferences"],
        "upload_profile_picture": ["upload_profile_picture"],
        "me": ["view_profile"],
        "profile": ["view_profile"],
        "search": ["search_users"],
    }
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["user__username", "user__email", "phone_number"]
    ordering_fields = ["created_at", "updated_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        # Optionally filter by query params (e.g., ?search=...)
        return queryset

    def get_serializer_class(self):
        if self.action == "update_profile":
            return UserProfileUpdateSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=["post"], permission_classes=[permissions.AllowAny])
    def register(self, request):
        """
        Register a new user and create a profile.
        """
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # UserProfile is created in serializer, but ensure existence
            UserProfile.objects.get_or_create(user=user)
            return Response(
                {"id": str(user.id), "email": user.email},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], permission_classes=[permissions.AllowAny])
    def login(self, request):
        """
        Authenticate user and return a success message or token.
        """
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]
            user = authenticate(request, email=email, password=password)
            if user:
                # Token generation (e.g., JWT) should be handled here
                return Response(
                    {"message": "Login successful", "user_id": str(user.id)},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True, methods=["patch"], permission_classes=[permissions.IsAuthenticated]
    )
    def update_profile(self, request, pk=None):
        """
        Update the user's profile (phone, picture, preferences).
        """
        profile = self.get_object()
        serializer = UserProfileUpdateSerializer(
            profile, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticated]
    )
    def profile(self, request, pk=None):
        """
        Retrieve the user's profile.
        """
        profile = self.get_object()
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request):
        """
        Get the profile of the currently authenticated user.
        """
        try:
            profile = UserProfile.objects.get(user=request.user)
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response(
                {"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAdminUser])
    def search(self, request):
        """
        Search for users by username, email, or phone number.
        """
        query = request.query_params.get("q", "")
        if not query:
            return Response(
                {"detail": "Query parameter 'q' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        profiles = UserProfile.objects.filter(
            Q(user__username__icontains=query)
            | Q(user__email__icontains=query)
            | Q(phone_number__icontains=query)
        )
        serializer = UserProfileSerializer(profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["patch"],
        permission_classes=[permissions.IsAuthenticated],
        url_path="preferences",
    )
    def update_preferences(self, request, pk=None):
        """
        Update user preferences.
        """
        profile = self.get_object()
        preferences = request.data.get("preferences")
        if preferences is not None:
            profile.preferences = preferences
            profile.save()
            return Response(
                {"preferences": profile.preferences}, status=status.HTTP_200_OK
            )
        return Response(
            {"detail": "No preferences provided."}, status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        url_path="upload-picture",
    )
    def upload_profile_picture(self, request, pk=None):
        """
        Upload or update the user's profile picture.
        """
        profile = self.get_object()
        file = request.FILES.get("profile_picture")
        if file:
            profile.profile_picture = file
            profile.save()
            return Response(
                {"profile_picture": profile.profile_picture.url},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"detail": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST
        )
