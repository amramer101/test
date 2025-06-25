from rest_framework import serializers
from apps.shared.serializers import BaseSerializer, DynamicFieldsSerializer
from .models import (
    ShopCategory,
    ShopItem,
    Purchase,
    PurchaseItem,
    UserInventory,
)
from apps.gamification.models import PointLedger
from apps.gamification.serializers import PointLedgerSerializer
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.openapi import OpenApiTypes

User = get_user_model()


class ShopCategorySerializer(BaseSerializer):
    item_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ShopCategory
        fields = [
            "id",
            "name",
            "description",
            "icon",
            "is_active",
            "sort_order",
            "item_count",
        ]


class ShopItemListSerializer(DynamicFieldsSerializer, serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    is_available = serializers.BooleanField(read_only=True)
    purchase_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ShopItem
        fields = [
            "id",
            "name",
            "category_name",
            "price_points",
            "is_available",
            "is_active",
            "purchase_count",
            "image",
        ]


class ShopItemSerializer(DynamicFieldsSerializer, serializers.ModelSerializer):
    category = ShopCategorySerializer(read_only=True)
    is_available = serializers.BooleanField(read_only=True)
    purchase_count = serializers.IntegerField(read_only=True)
    user_inventory_count = serializers.SerializerMethodField()

    class Meta:
        model = ShopItem
        fields = [
            "id",
            "name",
            "description",
            "category",
            "price_points",
            "inventory_count",
            "is_unlimited_inventory",
            "is_digital",
            "is_active",
            "image",
            "sort_order",
            "is_available",
            "purchase_count",
            "user_inventory_count",
        ]

    @extend_schema_field(OpenApiTypes.INT)
    def get_user_inventory_count(self, obj):
        user = self.context.get("request").user if self.context.get("request") else None
        if user and user.is_authenticated:
            inv = UserInventory.objects.filter(
                user=user, shop_item=obj, is_active=True
            ).first()
            return inv.quantity if inv else 0
        return 0

    def validate_price_points(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be positive.")
        return value


class PurchaseItemSerializer(DynamicFieldsSerializer, serializers.ModelSerializer):
    shop_item = ShopItemListSerializer(read_only=True)

    class Meta:
        model = PurchaseItem
        fields = ["id", "shop_item", "quantity", "points_per_item", "total_points"]


class PurchaseSerializer(DynamicFieldsSerializer, serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    items = PurchaseItemSerializer(many=True, read_only=True)
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Purchase
        fields = [
            "id",
            "user",
            "total_points_spent",
            "status",
            "purchased_at",
            "notes",
            "items",
            "item_count",
        ]

    @extend_schema_field(OpenApiTypes.INT)
    def get_item_count(self, obj):
        return obj.items.count()

    def validate(self, data):
        user = self.context["request"].user
        total_cost = 0
        for entry in data["items"]:
            item = entry["shop_item"]
            quantity = entry["quantity"]
            if not item.is_active:
                raise serializers.ValidationError(
                    f"Item '{item.name}' is not available."
                )
            if not item.is_unlimited_inventory and item.inventory_count < quantity:
                raise serializers.ValidationError(
                    f"Insufficient inventory for '{item.name}'."
                )
            total_cost += item.price_points * quantity
        # Points validation should be done in service, but can be checked here if balance is available in context
        if (
            hasattr(user, "pointprofile")
            and user.pointprofile.available_points < total_cost
        ):
            raise serializers.ValidationError("Insufficient points for this purchase.")
        return data


class PurchaseCreateItemSerializer(serializers.Serializer):
    shop_item = serializers.PrimaryKeyRelatedField(
        queryset=ShopItem.objects.filter(is_active=True)
    )
    quantity = serializers.IntegerField(min_value=1)

    def validate(self, data):
        item = data["shop_item"]
        quantity = data["quantity"]
        if not item.is_unlimited_inventory and item.inventory_count < quantity:
            raise serializers.ValidationError("Insufficient inventory for this item.")
        return data


class PurchaseCreateSerializer(serializers.Serializer):
    items = PurchaseCreateItemSerializer(many=True)

    def validate(self, data):
        user = self.context["request"].user
        total_cost = 0
        for entry in data["items"]:
            item = entry["shop_item"]
            quantity = entry["quantity"]
            if not item.is_active:
                raise serializers.ValidationError(
                    f"Item '{item.name}' is not available."
                )
            if not item.is_unlimited_inventory and item.inventory_count < quantity:
                raise serializers.ValidationError(
                    f"Insufficient inventory for '{item.name}'."
                )
            total_cost += item.price_points * quantity
        # Points validation should be done in service, but can be checked here if balance is available in context
        if (
            hasattr(user, "pointprofile")
            and user.pointprofile.available_points < total_cost
        ):
            raise serializers.ValidationError("Insufficient points for this purchase.")
        return data


class UserInventorySerializer(DynamicFieldsSerializer, serializers.ModelSerializer):
    shop_item = ShopItemListSerializer(read_only=True)

    class Meta:
        model = UserInventory
        fields = ["id", "user", "shop_item", "quantity", "acquired_at", "is_active"]
