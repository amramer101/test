from django.contrib import admin
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


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "content", "like_count", "is_published", "created_at")
    list_filter = ("is_published", "created_at")
    search_fields = ("content", "user__email")
    actions = ["approve_comments", "reject_comments"]

    def approve_comments(self, request, queryset):
        queryset.update(is_published=True)

    def reject_comments(self, request, queryset):
        queryset.update(is_published=False)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("user", "content_type", "object_id", "created_at")
    list_filter = ("content_type", "created_at")
    readonly_fields = ("user", "content_type", "object_id", "created_at")


@admin.register(Discussion)
class DiscussionAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "created_by",
        "reply_count",
        "view_count",
        "is_pinned",
        "is_locked",
    )
    list_filter = ("category", "is_pinned", "is_locked")
    search_fields = ("title", "description", "created_by__email")


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = (
        "referrer",
        "referred_email",
        "status",
        "points_awarded",
        "created_at",
        "completed_at",
    )
    list_filter = ("status", "completed_at")
    search_fields = ("referrer__email", "referred_email")


@admin.register(ActivityFeed)
class ActivityFeedAdmin(admin.ModelAdmin):
    list_display = ("user", "activity_type", "description", "is_public", "created_at")
    list_filter = ("activity_type", "is_public", "created_at")
    search_fields = ("user__email", "description")


@admin.register(DiscussionReply)
class DiscussionReplyAdmin(admin.ModelAdmin):
    list_display = (
        "discussion",
        "user",
        "content",
        "is_solution",
        "like_count",
        "created_at",
    )
    list_filter = ("is_solution", "created_at")
    search_fields = ("discussion__title", "user__email", "content")


@admin.register(UserFollowing)
class UserFollowingAdmin(admin.ModelAdmin):
    list_display = ("follower", "following", "created_at")
    list_filter = ("created_at",)
    search_fields = ("follower__email", "following__email")
