from django.db import models
from apps.shared.models import BaseModel
from django.conf import settings


class Role(BaseModel):
    """
    Role model for RBAC.
    """

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    permissions = models.ManyToManyField("Permission", related_name="roles", blank=True)

    def __str__(self):
        return self.name


class Permission(BaseModel):
    """
    Permission model for RBAC.
    """

    name = models.CharField(max_length=255, unique=True)
    codename = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


# ------------------------------------------------------------------------
# Enhanced Gamification, Social, and Shop Permissions for RBAC Integration
# ------------------------------------------------------------------------
#
# The following permissions should be created via data migration or admin:
#
# Enhanced Gamification Permissions:
#   - start_quest: Start new quests
#   - abandon_quest: Abandon active quests
#   - manage_quests: Admin quest management
#   - participate_events: Participate in time-limited events
#   - manage_events: Admin event management
#   - view_streaks: View streak information
#   - reset_streaks: Admin streak reset capability
#   - complete_challenges: Complete daily/weekly challenges
#   - manage_challenges: Admin challenge management
#   - award_manual_points: Manual point awarding (admin)
#   - adjust_user_balance: Balance adjustment capability
#
# Social Interaction Permissions:
#   - post_comments: Post comments on content
#   - moderate_comments: Moderate user comments
#   - like_content: Like posts, comments, courses
#   - share_content: Share content externally
#   - create_discussions: Start forum discussions
#   - moderate_discussions: Moderate forum content
#   - follow_users: Follow other users
#   - create_referrals: Generate referral codes
#   - view_activity_feed: Access activity feeds
#   - manage_social_privacy: Control social privacy settings
#
# Enhanced Shop Permissions:
#   - purchase_cosmetics: Buy cosmetic items
#   - equip_cosmetics: Equip purchased cosmetics
#   - gift_items: Gift items to other users
#   - manage_inventory: Admin inventory management
#
# These permissions integrate with the existing Role system and can be assigned
# to appropriate user roles (student, instructor, moderator, admin, etc.).
# No model structure changes needed, just new permission data.
#
# For automated creation, a data migration can be generated.
# ------------------------------------------------------------------------


class UserRole(BaseModel):
    """
    UserRole model for assigning roles to users.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_roles"
    )
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="user_roles")

    class Meta:
        unique_together = ("user", "role")
        verbose_name = "User Role"
        verbose_name_plural = "User Roles"

    def __str__(self):
        return f"{self.user.email} - {self.role.name}"
