from django.db import models
from django.conf import settings


class UserProfile(models.Model):
    """
    UserProfile model with OneToOne relationship to authentication.User.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    phone_number = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", blank=True, null=True
    )
    preferences = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    bio = models.TextField(blank=True)
    social_links = models.JSONField(default=dict, blank=True)
    selected_avatar = models.CharField(max_length=128, blank=True)
    selected_theme = models.CharField(max_length=64, default="default")
    display_badges = models.JSONField(default=list, blank=True)
    privacy_settings = models.JSONField(default=dict, blank=True)
    follower_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)
    social_score = models.PositiveIntegerField(default=0)
    unlocked_avatars = models.JSONField(default=list, blank=True)
    unlocked_themes = models.JSONField(default=list, blank=True)
    showcase_achievements = models.BooleanField(default=True)

    class Meta:
        db_table = "user_profiles"
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"Profile of {self.user.email}"

    def get_unlocked_cosmetics(self):
        return {
            "avatars": self.unlocked_avatars,
            "themes": self.unlocked_themes,
        }

    def can_use_cosmetic(self, cosmetic_type, cosmetic_id):
        if cosmetic_type == "avatar":
            return cosmetic_id in self.unlocked_avatars
        if cosmetic_type == "theme":
            return cosmetic_id in self.unlocked_themes
        return False

    def update_social_counts(self):
        from apps.social.models import UserFollowing

        self.follower_count = UserFollowing.objects.filter(following=self.user).count()
        self.following_count = UserFollowing.objects.filter(follower=self.user).count()
        self.save(update_fields=["follower_count", "following_count"])
