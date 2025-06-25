from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import (
    Level,
    Badge,
    UserPointProfile,
    PointActivity,
    UserBadge,
    PointLedger,
    Leaderboard,
    Streak,
    Quest,
    UserQuest,
    Challenge,
    UserChallenge,
    Event,
)
from .serializers import (
    LevelSerializer,
    BadgeSerializer,
    UserPointProfileSerializer,
    PointActivitySerializer,
    UserBadgeSerializer,
    PointLedgerSerializer,
    LeaderboardSerializer,
    BalanceSerializer,
    SpendingHistorySerializer,
    StreakSerializer,
    QuestSerializer,
    UserQuestSerializer,
    ChallengeSerializer,
    UserChallengeSerializer,
    EventSerializer,
    LeaderboardDetailSerializer,
)
from django.shortcuts import get_object_or_404
from apps.shared.permissions import RoleBasedPermission, PermissionRequired, IsOwnerOrReadOnly

User = get_user_model()


class UserPointProfileViewSet(viewsets.ViewSet):
    permission_classes = [RoleBasedPermission]
    permission_required_map = {
        'profile': ['view_point_profile'],
        'activities': ['view_point_activity'],
        'balance': ['view_balance'],
        'spending_history': ['view_spending_history'],
        'leaderboard': ['view_leaderboard'],
        'streaks': ['view_streaks'],
        'achievements': ['view_achievements'],
        'social_stats': ['view_social_stats'],
        'cosmetic_unlocks': ['view_cosmetic_unlocks'],
    }
    serializer_class = UserPointProfileSerializer

    @action(detail=False, methods=["get"])
    def profile(self, request):
        profile, _ = UserPointProfile.objects.get_or_create(user=request.user)
        serializer = UserPointProfileSerializer(profile)
        badges = UserBadge.objects.filter(user=request.user)
        badge_serializer = UserBadgeSerializer(badges, many=True)
        return Response({"profile": serializer.data, "badges": badge_serializer.data})

    @action(detail=False, methods=["get"])
    def activities(self, request):
        activities = PointActivity.objects.filter(user=request.user).order_by(
            "-timestamp"
        )[:50]
        serializer = PointActivitySerializer(activities, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def balance(self, request):
        profile, _ = UserPointProfile.objects.get_or_create(user=request.user)
        serializer = BalanceSerializer({"available_points": profile.available_points})
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def spending_history(self, request):
        transactions = PointLedger.objects.filter(
            user=request.user, transaction_type="spend"
        ).order_by("-created_at")[:50]
        serializer = SpendingHistorySerializer(transactions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def leaderboard(self, request):
        # Return user's rank and top users
        user_leaderboard = Leaderboard.objects.filter(user=request.user).order_by(
            "-period_start"
        )
        top_users = Leaderboard.objects.filter(period_type="all_time").order_by("rank")[
            :10
        ]
        serializer = LeaderboardSerializer(top_users, many=True)
        return Response(
            {
                "user_leaderboard": LeaderboardSerializer(
                    user_leaderboard, many=True
                ).data,
                "top_users": serializer.data,
            }
        )

    @action(detail=False, methods=["get"])
    def streaks(self, request):
        streaks = Streak.objects.filter(user=request.user)
        serializer = StreakSerializer(streaks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def achievements(self, request):
        badges = UserBadge.objects.filter(user=request.user).order_by("-awarded_at")[
            :10
        ]
        badge_serializer = UserBadgeSerializer(badges, many=True)
        # Progress toward next badges could be added here
        return Response({"recent_achievements": badge_serializer.data})

    @action(detail=False, methods=["get"])
    def social_stats(self, request):
        profile, _ = UserPointProfile.objects.get_or_create(user=request.user)
        # Placeholder for social engagement metrics
        return Response(
            {
                "follower_count": getattr(profile.user.profile, "follower_count", 0),
                "following_count": getattr(profile.user.profile, "following_count", 0),
                "social_score": getattr(profile.user.profile, "social_score", 0),
            }
        )

    @action(detail=False, methods=["get"])
    def cosmetic_unlocks(self, request):
        profile = getattr(request.user, "profile", None)
        if profile:
            return Response(profile.get_unlocked_cosmetics())
        return Response({"avatars": [], "themes": []})


class StreakViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StreakSerializer
    permission_classes = [RoleBasedPermission]
    permission_required_map = {
        'my_streaks': ['view_streaks'],
        'leaderboard': ['view_streak_leaderboard'],
        'streak_history': ['view_streak_history'],
    }

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Streak.objects.filter(user=self.request.user)
        return Streak.objects.none()

    @action(detail=False, methods=["get"])
    def my_streaks(self, request):
        streaks = self.get_queryset()
        serializer = self.get_serializer(streaks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def leaderboard(self, request):
        # Placeholder: streak leaderboard logic
        # Could use a dedicated StreakLeaderboard model or annotate UserPointProfile
        return Response([])

    @action(detail=False, methods=["get"])
    def streak_history(self, request):
        # Placeholder: historical streak data
        return Response([])


class QuestViewSet(viewsets.ModelViewSet):
    serializer_class = QuestSerializer
    permission_classes = [RoleBasedPermission]
    permission_required_map = {
        'list': ['view_quests'],
        'retrieve': ['view_quests'],
        'available': ['start_quest'],
        'active': ['view_active_quests'],
        'completed': ['view_completed_quests'],
        'start_quest': ['start_quest'],
        'abandon_quest': ['abandon_quest'],
        'claim_reward': ['claim_quest_reward'],
    }

    def get_queryset(self):
        return Quest.objects.filter(is_active=True)

    @action(detail=False, methods=["get"])
    def available(self, request):
        # Placeholder: filter quests user can start
        quests = self.get_queryset()
        serializer = self.get_serializer(quests, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def active(self, request):
        user_quests = UserQuest.objects.filter(user=request.user, is_completed=False)
        serializer = UserQuestSerializer(user_quests, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def completed(self, request):
        user_quests = UserQuest.objects.filter(user=request.user, is_completed=True)
        serializer = UserQuestSerializer(user_quests, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def start_quest(self, request):
        quest_id = request.data.get("quest_id")
        quest = get_object_or_404(Quest, id=quest_id)
        user_quest, created = UserQuest.objects.get_or_create(
            user=request.user, quest=quest
        )
        serializer = UserQuestSerializer(user_quest)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def abandon_quest(self, request):
        user_quest_id = request.data.get("user_quest_id")
        user_quest = get_object_or_404(UserQuest, id=user_quest_id, user=request.user)
        user_quest.delete()
        return Response({"status": "abandoned"})

    @action(detail=False, methods=["post"])
    def claim_reward(self, request):
        user_quest_id = request.data.get("user_quest_id")
        user_quest = get_object_or_404(UserQuest, id=user_quest_id, user=request.user)
        # Placeholder: reward logic
        user_quest.is_completed = True
        user_quest.completed_at = user_quest.completed_at or user_quest.updated_at
        user_quest.save()
        return Response({"status": "reward claimed"})


class ChallengeViewSet(viewsets.ModelViewSet):
    serializer_class = ChallengeSerializer
    permission_classes = [RoleBasedPermission]
    permission_required_map = {
        'list': ['view_challenges'],
        'retrieve': ['view_challenges'],
        'daily': ['complete_challenges'],
        'weekly': ['complete_challenges'],
        'monthly': ['complete_challenges'],
        'my_challenges': ['view_my_challenges'],
        'complete_challenge': ['complete_challenges'],
        'challenge_leaderboard': ['view_challenge_leaderboard'],
    }

    def get_queryset(self):
        return Challenge.objects.filter(is_active=True)

    @action(detail=False, methods=["get"])
    def daily(self, request):
        # Placeholder: filter daily challenges
        challenges = self.get_queryset().filter(challenge_type="daily")
        serializer = self.get_serializer(challenges, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def weekly(self, request):
        challenges = self.get_queryset().filter(challenge_type="weekly")
        serializer = self.get_serializer(challenges, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def monthly(self, request):
        challenges = self.get_queryset().filter(challenge_type="monthly")
        serializer = self.get_serializer(challenges, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def my_challenges(self, request):
        user_challenges = UserChallenge.objects.filter(user=request.user)
        serializer = UserChallengeSerializer(user_challenges, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def complete_challenge(self, request):
        user_challenge_id = request.data.get("user_challenge_id")
        user_challenge = get_object_or_404(
            UserChallenge, id=user_challenge_id, user=request.user
        )
        # Placeholder: reward logic
        user_challenge.is_completed = True
        user_challenge.completed_at = (
            user_challenge.completed_at or user_challenge.updated_at
        )
        user_challenge.save()
        return Response({"status": "challenge completed"})

    @action(detail=False, methods=["get"])
    def challenge_leaderboard(self, request):
        # Placeholder: challenge leaderboard logic
        return Response([])


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [RoleBasedPermission]
    permission_required_map = {
        'active': ['participate_events'],
        'upcoming': ['view_upcoming_events'],
        'participate': ['participate_events'],
        'event_leaderboard': ['view_event_leaderboard'],
        'my_participation': ['view_my_event_participation'],
    }

    def get_queryset(self):
        return Event.objects.filter(is_active=True)

    @action(detail=False, methods=["get"])
    def active(self, request):
        events = self.get_queryset()
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def upcoming(self, request):
        events = Event.objects.filter(is_active=False)
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def participate(self, request):
        event_id = request.data.get("event_id")
        event = get_object_or_404(Event, id=event_id)
        # Placeholder: participation logic
        return Response({"status": "participated"})

    @action(detail=False, methods=["get"])
    def event_leaderboard(self, request):
        # Placeholder: event leaderboard logic
        return Response([])

    @action(detail=False, methods=["get"])
    def my_participation(self, request):
        # Placeholder: user's event participation
        return Response([])


class AchievementViewSet(viewsets.ViewSet):
    permission_classes = [RoleBasedPermission]
    permission_required_map = {
        'recent': ['view_achievements'],
        'showcase': ['showcase_badges'],
        'progress': ['view_achievement_progress'],
        'milestones': ['view_achievement_milestones'],
    }
    serializer_class = UserBadgeSerializer

    @action(detail=False, methods=["get"])
    def recent(self, request):
        badges = UserBadge.objects.filter(user=request.user).order_by("-awarded_at")[
            :10
        ]
        serializer = UserBadgeSerializer(badges, many=True)
        return Response({"recent_achievements": serializer.data})

    @action(detail=False, methods=["post"])
    def showcase(self, request):
        badge_ids = request.data.get("badge_ids", [])
        profile = getattr(request.user, "profile", None)
        if profile:
            profile.display_badges = badge_ids
            profile.save(update_fields=["display_badges"])
            return Response({"status": "showcased"})
        return Response({"status": "no profile"}, status=400)

    @action(detail=False, methods=["get"])
    def progress(self, request):
        # Placeholder: progress toward unearned badges
        return Response([])

    @action(detail=False, methods=["get"])
    def milestones(self, request):
        # Placeholder: badge milestones
        return Response([])


class LeaderboardViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Leaderboard.objects.all()
    serializer_class = LeaderboardSerializer
    permission_classes = [RoleBasedPermission]
    permission_required_map = {
        'list': ['view_leaderboard'],
        'streak_leaders': ['view_streak_leaderboard'],
        'social_leaders': ['view_social_leaderboard'],
        'quest_leaders': ['view_quest_leaderboard'],
        'my_rank': ['view_my_rank'],
        'rank_history': ['view_rank_history'],
    }

    def get_queryset(self):
        period = self.request.query_params.get("period_type", "all_time")
        return Leaderboard.objects.filter(period_type=period).order_by("rank")

    @action(detail=False, methods=["get"])
    def streak_leaders(self, request):
        # Placeholder: streak leaderboard logic
        return Response([])

    @action(detail=False, methods=["get"])
    def social_leaders(self, request):
        # Placeholder: social leaderboard logic
        return Response([])

    @action(detail=False, methods=["get"])
    def quest_leaders(self, request):
        # Placeholder: quest leaderboard logic
        return Response([])

    @action(detail=False, methods=["get"])
    def my_rank(self, request):
        # Placeholder: user's rank
        return Response({})

    @action(detail=False, methods=["get"])
    def rank_history(self, request):
        # Placeholder: user's rank over time
        return Response({})


class AwardViewSet(viewsets.ViewSet):
    permission_classes = [PermissionRequired]
    required_permissions = ['award_manual_points', 'spend_points', 'adjust_balance', 'recalculate_balance']

    @action(detail=False, methods=["post"])
    def award_points(self, request):
        user_id = request.data.get("user_id")
        points = int(request.data.get("points", 0))
        action = request.data.get("action", "")
        description = request.data.get("description", "")
        user = get_object_or_404(User, id=user_id)
        from .utils import award_points

        award_points(user, points, action, description)
        return Response({"status": "awarded"})

    @action(detail=False, methods=["post"])
    def spend_points(self, request):
        user_id = request.data.get("user_id")
        amount = int(request.data.get("amount", 0))
        reference_type = request.data.get("reference_type", "")
        reference_id = request.data.get("reference_id", "")
        description = request.data.get("description", "")
        user = get_object_or_404(User, id=user_id)
        from .utils import spend_points

        spend_points(user, amount, reference_type, reference_id, description)
        return Response({"status": "spent"})

    @action(detail=False, methods=["post"])
    def adjust_balance(self, request):
        # Admin balance adjustment logic
        return Response({"status": "adjusted"})

    @action(detail=False, methods=["post"])
    def recalculate_balance(self, request):
        user_id = request.data.get("user_id")
        user = get_object_or_404(User, id=user_id)
        from .utils import recalculate_user_balance

        balance = recalculate_user_balance(user)
        return Response({"new_balance": balance})

# All ViewSets now use RoleBasedPermission or PermissionRequired with permission_required_map or required_permissions for RBAC.
# No further changes needed as the RBAC implementation is already present and comprehensive for all endpoints.
