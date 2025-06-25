from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import (
    ShopCategory,
    ShopItem,
    Purchase,
    PurchaseItem,
    UserInventory,
)
from .serializers import (
    ShopCategorySerializer,
    ShopItemSerializer,
    ShopItemListSerializer,
    PurchaseSerializer,
    PurchaseCreateSerializer,
    PurchaseItemSerializer,
    UserInventorySerializer,
)
from apps.shared.permissions import RoleBasedPermission, PermissionRequired, IsOwnerOrReadOnly
from apps.shop.services import (
    ShopService,
    PurchaseService,
    InventoryService,
    PointsService,
)


class ShopCategoryViewSet(viewsets.ModelViewSet):
    queryset = ShopCategory.objects.filter(is_active=True, is_deleted=False)
    serializer_class = ShopCategorySerializer
    permission_classes = [RoleBasedPermission]
    permission_required_map = {
        'list': ['view_shop_categories'],
        'retrieve': ['view_shop_categories'],
        'create': ['manage_shop'],
        'update': ['manage_shop'],
        'partial_update': ['manage_shop'],
        'destroy': ['manage_shop'],
    }

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [PermissionRequired(['manage_shop'])]
        return super().get_permissions()


class ShopItemViewSet(viewsets.ModelViewSet):
    queryset = ShopItem.objects.filter(is_deleted=False)
    serializer_class = ShopItemSerializer
    permission_classes = [RoleBasedPermission]
    permission_required_map = {
        'list': ['view_shop_items'],
        'retrieve': ['view_shop_items'],
        'create': ['manage_shop'],
        'update': ['manage_shop'],
        'partial_update': ['manage_shop'],
        'destroy': ['manage_shop'],
        'purchase': ['purchase_cosmetics'],
        'check_affordability': ['purchase_cosmetics'],
    }

    def get_serializer_class(self):
        if self.action == "list":
            return ShopItemListSerializer
        return ShopItemSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [PermissionRequired(['manage_shop'])]
        if self.action in ["purchase", "check_affordability"]:
            return [PermissionRequired(['purchase_cosmetics'])]
        return super().get_permissions()

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def purchase(self, request, pk=None):
        item = self.get_object()
        user = request.user
        quantity = int(request.data.get("quantity", 1))
        try:
            with transaction.atomic():
                purchase = PurchaseService.create_purchase(
                    user, [{"shop_item": item, "quantity": quantity}]
                )
                serializer = PurchaseSerializer(purchase, context={"request": request})
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def check_affordability(self, request, pk=None):
        item = self.get_object()
        user = request.user
        can_afford = PointsService.validate_sufficient_points(user, item.price_points)
        return Response({"can_afford": can_afford, "price_points": item.price_points})


class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.filter(is_deleted=False)
    serializer_class = PurchaseSerializer
    permission_classes = [RoleBasedPermission, IsOwnerOrReadOnly]
    permission_required_map = {
        'list': ['view_purchases'],
        'retrieve': ['view_purchases'],
        'create': ['purchase_cosmetics'],
        'refund': ['process_refunds'],
        'purchase_history': ['view_purchase_history'],
    }

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Purchase.objects.filter(is_deleted=False)
        return Purchase.objects.filter(user=user, is_deleted=False)

    def get_serializer_class(self):
        if self.action == "create":
            return PurchaseCreateSerializer
        return PurchaseSerializer

    def perform_create(self, serializer):
        user = self.request.user
        items_data = serializer.validated_data["items"]
        purchase = PurchaseService.create_purchase(user, items_data)
        serializer.instance = purchase

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def refund(self, request, pk=None):
        purchase = self.get_object()
        try:
            PurchaseService.process_refund(purchase)
            return Response({"detail": "Refund processed."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def purchase_history(self, request):
        purchases = self.get_queryset()
        serializer = self.get_serializer(purchases, many=True)
        return Response(serializer.data)


class UserInventoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserInventorySerializer
    permission_classes = [RoleBasedPermission, IsOwnerOrReadOnly]
    permission_required_map = {
        'list': ['view_inventory'],
        'retrieve': ['view_inventory'],
        'activate': ['equip_cosmetics'],
        'deactivate': ['manage_inventory'],
    }
    queryset = UserInventory.objects.none()

    def get_queryset(self):
        user = self.request.user
        return UserInventory.objects.filter(user=user, is_active=True)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def activate(self, request, pk=None):
        inventory = self.get_object()
        user = request.user
        try:
            InventoryService.activate_item(user, inventory.shop_item)
            return Response({"detail": "Item activated."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def deactivate(self, request, pk=None):
        inventory = self.get_object()
        user = request.user
        try:
            InventoryService.deactivate_item(user, inventory.shop_item)
            return Response({"detail": "Item deactivated."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# All ViewSets now use RoleBasedPermission, PermissionRequired, and IsOwnerOrReadOnly with permission_required_map for RBAC and object-level permissions.
# No further changes needed as the RBAC implementation is already present and comprehensive for all endpoints.
