from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from django.urls import path, include

from .views import (
    ShopCategoryViewSet,
    ShopItemViewSet,
    PurchaseViewSet,
    UserInventoryViewSet,
)

app_name = "shop"

# Main router
router = DefaultRouter()
router.register(r"categories", ShopCategoryViewSet, basename="shop-category")
router.register(r"items", ShopItemViewSet, basename="shop-item")
router.register(r"purchases", PurchaseViewSet, basename="purchase")
router.register(r"inventory", UserInventoryViewSet, basename="user-inventory")

urlpatterns = [
    path("", include(router.urls)),
]
