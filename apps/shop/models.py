from django.db import models
from django.conf import settings
from apps.shared.models import BaseModel
from apps.authentication.models import User


class ShopCategory(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.ImageField(upload_to="shop/icons/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    def item_count(self):
        return self.items.filter(is_active=True).count()

    def active_items(self):
        return self.items.filter(is_active=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["sort_order", "name"]


class ShopItem(BaseModel):
    category = models.ForeignKey(
        ShopCategory, on_delete=models.SET_NULL, null=True, related_name="items"
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    price_points = models.PositiveIntegerField()
    inventory_count = models.PositiveIntegerField(default=0)
    is_unlimited_inventory = models.BooleanField(default=False)
    is_digital = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to="shop/items/", blank=True, null=True)
    sort_order = models.PositiveIntegerField(default=0)
    unlock_level = models.IntegerField(null=True, blank=True)
    unlock_badge = models.ForeignKey(
        "gamification.Badge", null=True, blank=True, on_delete=models.SET_NULL
    )
    ITEM_TYPE_CHOICES = [
        ("consumable", "Consumable"),
        ("cosmetic_avatar", "Cosmetic Avatar"),
        ("cosmetic_theme", "Cosmetic Theme"),
        ("course_unlock", "Course Unlock"),
        ("feature_unlock", "Feature Unlock"),
    ]
    item_type = models.CharField(
        max_length=32, choices=ITEM_TYPE_CHOICES, default="consumable"
    )
    is_limited_time = models.BooleanField(default=False)
    event = models.ForeignKey(
        "gamification.Event", null=True, blank=True, on_delete=models.SET_NULL
    )
    cosmetic_data = models.JSONField(default=dict, blank=True)

    def is_available(self):
        return self.is_active and (
            self.is_unlimited_inventory or self.inventory_count > 0
        )

    def purchase_count(self):
        return self.purchase_items.count()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["sort_order", "name"]


class Purchase(BaseModel):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="purchases")
    total_points_spent = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    purchased_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def add_item(self, shop_item, quantity, points_per_item):
        PurchaseItem.objects.create(
            purchase=self,
            shop_item=shop_item,
            quantity=quantity,
            points_per_item=points_per_item,
            total_points=quantity * points_per_item,
        )

    def calculate_total(self):
        return sum(item.total_points for item in self.items.all())

    def __str__(self):
        return f"{self.user} - {self.total_points_spent} points"

    class Meta:
        ordering = ["-purchased_at"]


class PurchaseItem(BaseModel):
    purchase = models.ForeignKey(
        Purchase, on_delete=models.CASCADE, related_name="items"
    )
    shop_item = models.ForeignKey(
        ShopItem, on_delete=models.CASCADE, related_name="purchase_items"
    )
    quantity = models.PositiveIntegerField()
    points_per_item = models.PositiveIntegerField()
    total_points = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.shop_item} x{self.quantity}"

    class Meta:
        ordering = ["purchase"]


class UserInventory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="inventory"
    )
    shop_item = models.ForeignKey(
        ShopItem, on_delete=models.CASCADE, related_name="user_inventories"
    )
    quantity = models.PositiveIntegerField(default=1)
    acquired_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    equipped = models.BooleanField(default=False)
    expiry_date = models.DateTimeField(null=True, blank=True)
    usage_count = models.PositiveIntegerField(default=0)
    max_uses = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.shop_item} ({self.quantity})"

    class Meta:
        ordering = ["-acquired_at"]
        unique_together = ("user", "shop_item")


class CosmeticUnlock(BaseModel):
    COSMETIC_TYPE_CHOICES = [
        ("avatar", "Avatar"),
        ("theme", "Theme"),
        ("badge_frame", "Badge Frame"),
    ]
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="cosmetic_unlocks"
    )
    cosmetic_type = models.CharField(max_length=32, choices=COSMETIC_TYPE_CHOICES)
    cosmetic_id = models.CharField(max_length=128)
    unlock_method = models.CharField(
        max_length=32,
        choices=[
            ("purchase", "Purchase"),
            ("achievement", "Achievement"),
            ("event", "Event"),
        ],
    )
    unlocked_at = models.DateTimeField(auto_now_add=True)
    is_equipped = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user", "cosmetic_type", "cosmetic_id")
