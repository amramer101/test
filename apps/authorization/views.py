from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from apps.authorization.models import Role, Permission, UserRole
from apps.authorization.serializers import (
    RoleSerializer,
    PermissionSerializer,
    UserRoleSerializer,
    RoleAssignmentSerializer,
    PermissionAssignmentSerializer,
)

User = get_user_model()


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(
        detail=True,
        methods=["post"],
        url_path="assign",
        permission_classes=[permissions.IsAdminUser],
    )
    def assign_role(self, request, pk=None):
        user_id = request.data.get("user_id")
        if not user_id:
            return Response(
                {"detail": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        role = self.get_object()
        user = get_object_or_404(User, id=user_id)
        if UserRole.objects.filter(user=user, role=role).exists():
            return Response(
                {"detail": "User already has this role."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        UserRole.objects.create(user=user, role=role)
        return Response({"detail": "Role assigned."}, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["post"],
        url_path="remove",
        permission_classes=[permissions.IsAdminUser],
    )
    def remove_role(self, request, pk=None):
        user_id = request.data.get("user_id")
        if not user_id:
            return Response(
                {"detail": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        role = self.get_object()
        user = get_object_or_404(User, id=user_id)
        deleted, _ = UserRole.objects.filter(user=user, role=role).delete()
        if deleted:
            return Response({"detail": "Role removed."}, status=status.HTTP_200_OK)
        return Response(
            {"detail": "Role not found for user."}, status=status.HTTP_404_NOT_FOUND
        )


class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(
        detail=True,
        methods=["post"],
        url_path="assign",
        permission_classes=[permissions.IsAdminUser],
    )
    def assign_permission(self, request, pk=None):
        user_id = request.data.get("user_id")
        if not user_id:
            return Response(
                {"detail": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        permission = self.get_object()
        user = get_object_or_404(User, id=user_id)
        if user.user_permissions.filter(id=permission.id).exists():
            return Response(
                {"detail": "User already has this permission."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.user_permissions.add(permission)
        return Response({"detail": "Permission assigned."}, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["post"],
        url_path="remove",
        permission_classes=[permissions.IsAdminUser],
    )
    def remove_permission(self, request, pk=None):
        user_id = request.data.get("user_id")
        if not user_id:
            return Response(
                {"detail": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        permission = self.get_object()
        user = get_object_or_404(User, id=user_id)
        if not user.user_permissions.filter(id=permission.id).exists():
            return Response(
                {"detail": "User does not have this permission."},
                status=status.HTTP_404_NOT_FOUND,
            )
        user.user_permissions.remove(permission)
        return Response({"detail": "Permission removed."}, status=status.HTTP_200_OK)


class UserRoleViewSet(viewsets.ModelViewSet):
    queryset = UserRole.objects.select_related("user", "role").all()
    serializer_class = UserRoleSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(
        detail=False,
        methods=["post"],
        url_path="by-user",
        permission_classes=[permissions.IsAuthenticated],
    )
    def list_roles_for_user(self, request):
        user_id = request.data.get("user_id")
        if not user_id:
            return Response(
                {"detail": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        user = get_object_or_404(User, id=user_id)
        roles = UserRole.objects.filter(user=user)
        serializer = self.get_serializer(roles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
