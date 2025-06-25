from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CommentViewSet,
    LikeViewSet,
    ShareViewSet,
    DiscussionViewSet,
    DiscussionReplyViewSet,
    ReferralViewSet,
    UserFollowingViewSet,
    ActivityFeedViewSet,
)

router = DefaultRouter()
router.register(r"comments", CommentViewSet, basename="social-comments")
router.register(r"likes", LikeViewSet, basename="social-likes")
router.register(r"shares", ShareViewSet, basename="social-shares")
router.register(r"discussions", DiscussionViewSet, basename="social-discussions")
router.register(
    r"discussion-replies", DiscussionReplyViewSet, basename="social-discussion-replies"
)
router.register(r"referrals", ReferralViewSet, basename="social-referrals")
router.register(r"following", UserFollowingViewSet, basename="social-following")
router.register(r"feed", ActivityFeedViewSet, basename="social-feed")

app_name = "social"

urlpatterns = [
    path("", include(router.urls)),
]
