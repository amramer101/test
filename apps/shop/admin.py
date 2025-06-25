from django.contrib import admin
from .models import (
    ShopCategory,
    ShopItem,
    Purchase,
    PurchaseItem,
    UserInventory,
)


class ShopItemInline(admin.TabularInline):
    model = ShopItem
    extra = 1
    fields = ("name", "price_points", "inventory_count", "is_active", "sort_order")
    show_change_link = True


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 0
    fields = ("shop_item", "quantity", "points_per_item", "total_points")
    readonly_fields = ("points_per_item", "total_points")
    show_change_link = True


@admin.register(ShopCategory)
class ShopCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "item_count", "is_active", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("name",)
    ordering = ("sort_order", "name")
    inlines = [ShopItemInline]


@admin.register(ShopItem)
class ShopItemAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price_points",
        "inventory_count",
        "is_unlimited_inventory",
        "is_digital",
        "is_active",
        "purchase_count",
        "sort_order",
    )
    list_filter = ("category", "is_active", "is_digital", "is_unlimited_inventory")
    search_fields = ("name", "description")
    ordering = ("sort_order", "name")
    readonly_fields = ("purchase_count",)
    actions = ["mark_active", "mark_inactive"]

    def mark_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} item(s) marked as active.")

    mark_active.short_description = "Mark selected items as active"

    def mark_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} item(s) marked as inactive.")

    mark_inactive.short_description = "Mark selected items as inactive"


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "total_points_spent",
        "status",
        "purchased_at",
        "item_count",
    )
    list_filter = ("status", "purchased_at")
    search_fields = ("user__username", "notes")
    ordering = ("-purchased_at",)
    readonly_fields = ("total_points_spent", "item_count")
    inlines = [PurchaseItemInline]

    def item_count(self, obj):
        return obj.items.count()

    item_count.short_description = "Items"


@admin.register(UserInventory)
class UserInventoryAdmin(admin.ModelAdmin):
    list_display = ("user", "shop_item", "quantity", "acquired_at", "is_active")
    list_filter = ("is_active", "shop_item")
    search_fields = ("user__username", "shop_item__name")
    ordering = ("-acquired_at",)
