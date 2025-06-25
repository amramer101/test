from rest_framework import serializers
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
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.openapi import OpenApiTypes


class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ["id", "number", "name", "required_points"]


class BadgeSerializer(serializers.ModelSerializer):
    criteria_breakdown = serializers.SerializerMethodField()

    class Meta:
        model = Badge
        fields = [
            "id",
            "name",
            "description",
            "icon",
            "criteria",
            "badge_type",
            "rarity",
            "unlock_level",
            "criteria_breakdown",
        ]

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_criteria_breakdown(self, obj):
        # Human-readable criteria breakdown
        return obj.criteria


class UserPointProfileSerializer(serializers.ModelSerializer):
    current_level = LevelSerializer(read_only=True)
    available_points = serializers.IntegerField(read_only=True)
    streak_count = serializers.IntegerField(read_only=True)
    longest_streak = serializers.IntegerField(read_only=True)
    consecutive_login_days = serializers.IntegerField(read_only=True)
    next_level_cost = serializers.SerializerMethodField()
    recent_activity_summary = serializers.SerializerMethodField()

    class Meta:
        model = UserPointProfile
        fields = [
            "id",
            "user",
            "total_points",
            "available_points",
            "current_level",
            "progress_to_next_level",
            "streak_count",
            "longest_streak",
            "consecutive_login_days",
            "next_level_cost",
            "recent_activity_summary",
        ]

    @extend_schema_field(OpenApiTypes.INT)
    def get_next_level_cost(self, obj):
        if obj.current_level:
            next_level = (
                Level.objects.filter(
                    required_points__gt=obj.current_level.required_points
                )
                .order_by("required_points")
                .first()
            )
            if next_level:
                return next_level.required_points - obj.total_points
        return None

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_recent_activity_summary(self, obj):
        return (
            PointActivity.objects.filter(user=obj.user)
            .order_by("-timestamp")[:5]
            .values("action", "points", "timestamp")
        )


class PointActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = PointActivity
        fields = [
            "id",
            "user",
            "action",
            "points",
            "transaction_type",
            "reference_type",
            "reference_id",
            "timestamp",
            "description",
        ]


class UserBadgeSerializer(serializers.ModelSerializer):
    badge = BadgeSerializer(read_only=True)

    class Meta:
        model = UserBadge
        fields = ["id", "user", "badge", "awarded_at"]


class PointLedgerSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointLedger
        fields = "__all__"


class StreakSerializer(serializers.ModelSerializer):
    streak_type = serializers.CharField()
    days_remaining = serializers.SerializerMethodField()
    milestone = serializers.SerializerMethodField()

    class Meta:
        model = Streak
        fields = [
            "id",
            "user",
            "streak_type",
            "current_count",
            "longest_count",
            "last_activity_date",
            "is_active",
            "days_remaining",
            "milestone",
            "created_at",
            "updated_at",
        ]

    @extend_schema_field(OpenApiTypes.INT)
    def get_days_remaining(self, obj):
        # Placeholder: calculate days remaining to maintain streak
        return getattr(obj, "days_remaining", None)

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_milestone(self, obj):
        # Placeholder: milestone info
        return getattr(obj, "milestone", None)


class QuestSerializer(serializers.ModelSerializer):
    badge_reward = BadgeSerializer(read_only=True)
    criteria = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Quest
        fields = [
            "id",
            "name",
            "description",
            "criteria",
            "points_reward",
            "badge_reward",
            "is_active",
            "start_date",
            "end_date",
            "difficulty_level",
            "progress",
            "created_at",
            "updated_at",
        ]

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_criteria(self, obj):
        return getattr(obj, "criteria", {})

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_progress(self, obj):
        # Placeholder: implement actual progress calculation
        return getattr(obj, "progress", 0)


class UserQuestSerializer(serializers.ModelSerializer):
    quest = QuestSerializer(read_only=True)
    completion_percentage = serializers.SerializerMethodField()
    time_remaining = serializers.SerializerMethodField()
    next_milestone = serializers.SerializerMethodField()

    class Meta:
        model = UserQuest
        fields = [
            "id",
            "user",
            "quest",
            "progress",
            "is_completed",
            "completed_at",
            "started_at",
            "completion_percentage",
            "time_remaining",
            "next_milestone",
            "created_at",
            "updated_at",
        ]

    def get_completion_percentage(self, obj):
        # Placeholder: calculate percent complete
        return getattr(obj, "completion_percentage", 0)

    def get_time_remaining(self, obj):
        # Placeholder: time left to complete quest
        return getattr(obj, "time_remaining", None)

    def get_next_milestone(self, obj):
        # Placeholder: next milestone info
        return getattr(obj, "next_milestone", None)


class ChallengeSerializer(serializers.ModelSerializer):
    criteria = serializers.SerializerMethodField()
    period_info = serializers.SerializerMethodField()

    class Meta:
        model = Challenge
        fields = [
            "id",
            "name",
            "description",
            "challenge_type",
            "criteria",
            "points_reward",
            "is_active",
            "period_duration",
            "period_info",
            "created_at",
            "updated_at",
        ]

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_criteria(self, obj):
        return getattr(obj, "criteria", {})

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_period_info(self, obj):
        # Placeholder: period info
        return getattr(obj, "period_info", None)


class UserChallengeSerializer(serializers.ModelSerializer):
    challenge = ChallengeSerializer(read_only=True)
    completion_status = serializers.SerializerMethodField()
    time_remaining = serializers.SerializerMethodField()

    class Meta:
        model = UserChallenge
        fields = [
            "id",
            "user",
            "challenge",
            "progress",
            "is_completed",
            "completed_at",
            "period_start",
            "period_end",
            "completion_status",
            "time_remaining",
            "created_at",
            "updated_at",
        ]

    def get_completion_status(self, obj):
        # Placeholder: status
        return getattr(obj, "completion_status", None)

    def get_time_remaining(self, obj):
        # Placeholder: time left in period
        return getattr(obj, "time_remaining", None)


class EventSerializer(serializers.ModelSerializer):
    special_rewards = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "id",
            "name",
            "description",
            "event_type",
            "point_multiplier",
            "start_date",
            "end_date",
            "is_active",
            "special_rewards",
            "created_at",
            "updated_at",
        ]

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_special_rewards(self, obj):
        return getattr(obj, "special_rewards", {})


class LeaderboardDetailSerializer(serializers.Serializer):
    user = serializers.CharField()
    rank = serializers.IntegerField()
    points = serializers.IntegerField()
    streak = serializers.IntegerField(required=False)
    social_score = serializers.IntegerField(required=False)
    rank_change = serializers.IntegerField(required=False)
    period_points = serializers.IntegerField(required=False)
    achievement_highlights = serializers.ListField(
        child=serializers.CharField(), required=False
    )


class LeaderboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leaderboard
        fields = "__all__"


class BalanceSerializer(serializers.Serializer):
    available_points = serializers.IntegerField()


class SpendingHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PointLedger
        fields = [
            "id",
            "transaction_type",
            "points",
            "balance_after",
            "reference_type",
            "reference_id",
            "description",
            "created_at",
        ]
