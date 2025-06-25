from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import ShopItem, Purchase, PurchaseItem, UserInventory
from apps.gamification.utils import (
    spend_points,
    get_user_balance,
    validate_sufficient_points,
)
from apps.shared.exceptions import BusinessLogicError
from apps.gamification.models import PointLedger


class ShopService:
    @staticmethod
    def get_available_items(user=None):
        # Optionally filter by user eligibility
        return ShopItem.objects.filter(is_active=True, is_deleted=False)

    @staticmethod
    def check_item_availability(item, quantity):
        if not item.is_active:
            raise BusinessLogicError("Item is not available.")
        if not item.is_unlimited_inventory and item.inventory_count < quantity:
            raise BusinessLogicError("Insufficient inventory for this item.")
        return True

    @staticmethod
    def calculate_user_affordability(user, items):
        total_cost = sum(
            item["shop_item"].price_points * item["quantity"] for item in items
        )
        balance = get_user_balance(user)
        return balance >= total_cost


class PurchaseService:
    @staticmethod
    @transaction.atomic
    def create_purchase(user, items_data):
        """
        items_data: list of dicts with keys 'shop_item' (ShopItem instance) and 'quantity' (int)
        """
        total_points = 0
        for entry in items_data:
            ShopService.check_item_availability(entry["shop_item"], entry["quantity"])
            total_points += entry["shop_item"].price_points * entry["quantity"]

        validate_sufficient_points(user, total_points)

        purchase = Purchase.objects.create(
            user=user,
            total_points_spent=total_points,
            status="completed",
            purchased_at=timezone.now(),
        )

        for entry in items_data:
            item = entry["shop_item"]
            quantity = entry["quantity"]
            PurchaseItem.objects.create(
                purchase=purchase,
                shop_item=item,
                quantity=quantity,
                points_per_item=item.price_points,
                total_points=item.price_points * quantity,
            )
            # Update inventory if not unlimited
            if not item.is_unlimited_inventory:
                item.inventory_count -= quantity
                item.save(update_fields=["inventory_count"])
            # Grant digital item to user
            if item.is_digital:
                InventoryService.grant_digital_item(user, item, quantity)

        # Deduct points from user
        spend_points(
            user,
            total_points,
            reference_type="purchase",
            reference_id=str(purchase.id),
            description="Shop purchase",
        )
        return purchase

    @staticmethod
    @transaction.atomic
    def process_refund(purchase):
        if purchase.status != "completed":
            raise BusinessLogicError("Only completed purchases can be refunded.")
        # Refund points to user
        user = purchase.user
        total_points = purchase.total_points_spent
        # Create refund transaction in PointLedger
        PointLedger.objects.create(
            user=user,
            transaction_type="refund",
            points=total_points,
            balance_after=get_user_balance(user) + total_points,
            reference_type="purchase",
            reference_id=str(purchase.id),
            description="Refunded purchase",
        )
        # Update purchase status
        purchase.status = "refunded"
        purchase.save(update_fields=["status"])
        # Optionally, restore inventory and deactivate digital items
        for item in purchase.items.all():
            shop_item = item.shop_item
            if not shop_item.is_unlimited_inventory:
                shop_item.inventory_count += item.quantity
                shop_item.save(update_fields=["inventory_count"])
            if shop_item.is_digital:
                inv = UserInventory.objects.filter(
                    user=user, shop_item=shop_item
                ).first()
                if inv:
                    inv.is_active = False
                    inv.save(update_fields=["is_active"])


class InventoryService:
    @staticmethod
    def grant_digital_item(user, item, quantity):
        inv, created = UserInventory.objects.get_or_create(user=user, shop_item=item)
        if created:
            inv.quantity = quantity
        else:
            inv.quantity += quantity
        inv.is_active = True
        inv.acquired_at = timezone.now()
        inv.save()

    @staticmethod
    def check_user_inventory(user, item):
        inv = UserInventory.objects.filter(
            user=user, shop_item=item, is_active=True
        ).first()
        return inv.quantity if inv else 0

    @staticmethod
    def activate_item(user, item):
        inv = UserInventory.objects.filter(user=user, shop_item=item).first()
        if not inv:
            raise BusinessLogicError("You do not own this item.")
        inv.is_active = True
        inv.save(update_fields=["is_active"])

    @staticmethod
    def deactivate_item(user, item):
        inv = UserInventory.objects.filter(user=user, shop_item=item).first()
        if not inv:
            raise BusinessLogicError("You do not own this item.")
        inv.is_active = False
        inv.save(update_fields=["is_active"])


class PointsService:
    @staticmethod
    def spend_points(user, amount, reference_type, reference_id):
        spend_points(
            user, amount, reference_type, reference_id, description="Shop purchase"
        )

    @staticmethod
    def get_user_balance(user):
        return get_user_balance(user)

    @staticmethod
    def validate_sufficient_points(user, amount):
        return validate_sufficient_points(user, amount)
