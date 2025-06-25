from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserPointProfileViewSet,
    LeaderboardViewSet,
    StreakViewSet,
    QuestViewSet,
    ChallengeViewSet,
    EventViewSet,
    AchievementViewSet,
)

router = DefaultRouter()
router.register(r"profile", UserPointProfileViewSet, basename="gamification-profile")
router.register(r"leaderboard", LeaderboardViewSet, basename="gamification-leaderboard")
router.register(r"streaks", StreakViewSet, basename="gamification-streaks")
router.register(r"quests", QuestViewSet, basename="gamification-quests")
router.register(r"challenges", ChallengeViewSet, basename="gamification-challenges")
router.register(r"events", EventViewSet, basename="gamification-events")
router.register(
    r"achievements", AchievementViewSet, basename="gamification-achievements"
)

urlpatterns = [
    path("", include(router.urls)),
]
