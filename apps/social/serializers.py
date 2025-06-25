from rest_framework import serializers
from .models import (
    Comment,
    Like,
    Share,
    Discussion,
    DiscussionReply,
    Referral,
    UserFollowing,
    ActivityFeed,
)
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field, extend_schema_serializer
from drf_spectacular.openapi import OpenApiTypes

User = get_user_model()


@extend_schema_serializer(component_name="SocialUser")
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    reply_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "user",
            "content",
            "parent_comment",
            "is_published",
            "like_count",
            "report_count",
            "created_at",
            "reply_count",
        ]

    @extend_schema_field(OpenApiTypes.INT)
    def get_reply_count(self, obj) -> int:
        return obj.replies.count()


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["content", "parent_comment"]


class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ["id", "user", "created_at"]


class ShareSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Share
        fields = ["id", "user", "share_type", "shared_at"]


class DiscussionSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Discussion
        fields = [
            "id",
            "title",
            "description",
            "category",
            "created_by",
            "is_pinned",
            "is_locked",
            "view_count",
            "reply_count",
            "created_at",
        ]


class DiscussionReplySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = DiscussionReply
        fields = [
            "id",
            "discussion",
            "user",
            "content",
            "parent_reply",
            "is_solution",
            "like_count",
            "created_at",
        ]


class ReferralSerializer(serializers.ModelSerializer):
    referrer = UserSerializer(read_only=True)
    referred_user = UserSerializer(read_only=True)

    class Meta:
        model = Referral
        fields = [
            "id",
            "referrer",
            "referred_email",
            "referred_user",
            "referral_code",
            "status",
            "points_awarded",
            "completed_at",
            "created_at",
        ]


class UserFollowingSerializer(serializers.ModelSerializer):
    follower = UserSerializer(read_only=True)
    following = UserSerializer(read_only=True)

    class Meta:
        model = UserFollowing
        fields = ["id", "follower", "following", "created_at"]


class ActivityFeedSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ActivityFeed
        fields = [
            "id",
            "user",
            "activity_type",
            "description",
            "is_public",
            "created_at",
        ]
