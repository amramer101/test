from django.db import models
from django.conf import settings
from apps.shared.models import BaseModel


class Level(models.Model):
    number = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=100)
    required_points = models.PositiveIntegerField()

    class Meta:
        ordering = ["number"]

    def __str__(self):
        return f"Level {self.number}: {self.name} ({self.required_points} pts)"


class Badge(models.Model):
    BADGE_TYPE_CHOICES = [
        ("achievement", "Achievement"),
        ("milestone", "Milestone"),
        ("social", "Social"),
        ("spending", "Spending"),
    ]
    RARITY_CHOICES = [
        ("common", "Common"),
        ("rare", "Rare"),
        ("epic", "Epic"),
        ("legendary", "Legendary"),
    ]
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.ImageField(upload_to="badges/")
    criteria = models.JSONField(help_text="Criteria for awarding this badge")
    badge_type = models.CharField(
        max_length=20, choices=BADGE_TYPE_CHOICES, default="achievement"
    )
    rarity = models.CharField(max_length=20, choices=RARITY_CHOICES, default="common")
    unlock_level = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name


class UserPointProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="point_profile"
    )
    total_points = models.PositiveIntegerField(default=0)
    available_points = models.IntegerField(default=0)
    current_level = models.ForeignKey(
        Level, on_delete=models.SET_NULL, null=True, blank=True
    )
    progress_to_next_level = models.FloatField(default=0.0)
    # Enhanced streak and social fields
    streak_count = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_login_date = models.DateField(null=True, blank=True)
    consecutive_login_days = models.IntegerField(default=0)

    def can_spend(self, amount):
        return self.available_points >= amount

    def update_available_points(self):
        # Recalculate from PointLedger
        balance = (
            PointLedger.objects.filter(user=self.user).order_by("-created_at").first()
        )
        self.available_points = balance.balance_after if balance else 0
        self.save(update_fields=["available_points"])

    def __str__(self):
        return f"{self.user.email} - {self.total_points} pts"


class PointActivity(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ("earn", "Earn"),
        ("spend", "Spend"),
        ("adjustment", "Adjustment"),
        ("refund", "Refund"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    points = models.IntegerField()  # Now supports negative values
    transaction_type = models.CharField(
        max_length=20, choices=TRANSACTION_TYPE_CHOICES, default="earn"
    )
    reference_type = models.CharField(max_length=50, blank=True)
    reference_id = models.CharField(max_length=50, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return (
            f"{self.user.email}: {self.action} ({self.transaction_type} {self.points})"
        )


class PointLedger(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ("earn", "Earn"),
        ("spend", "Spend"),
        ("adjustment", "Adjustment"),
        ("refund", "Refund"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    points = models.IntegerField()
    balance_after = models.IntegerField()
    reference_type = models.CharField(max_length=50, blank=True)
    reference_id = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.transaction_type} {self.points} (bal: {self.balance_after})"

    class Meta:
        ordering = ["-created_at"]


class Leaderboard(models.Model):
    PERIOD_TYPE_CHOICES = [
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
        ("all_time", "All Time"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    period_type = models.CharField(max_length=20, choices=PERIOD_TYPE_CHOICES)
    points_earned = models.IntegerField(default=0)
    rank = models.PositiveIntegerField(default=0)
    period_start = models.DateField()
    period_end = models.DateField()

    class Meta:
        unique_together = ("user", "period_type", "period_start")
        ordering = ["period_type", "-period_start", "rank"]

    def __str__(self):
        return f"{self.user.email} - {self.period_type} #{self.rank} ({self.points_earned} pts)"


class UserBadge(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "badge")

    def __str__(self):
        return f"{self.user.email} - {self.badge.name}"


# --- Streak Model ---
class Streak(BaseModel):
    STREAK_TYPE_CHOICES = [
        ("login", "Login"),
        ("activity", "Activity"),
        ("lesson_completion", "Lesson Completion"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    streak_type = models.CharField(max_length=32, choices=STREAK_TYPE_CHOICES)
    current_count = models.IntegerField(default=0)
    longest_count = models.IntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("user", "streak_type")


# --- Quest Model ---
class Quest(BaseModel):
    DIFFICULTY_CHOICES = [
        ("easy", "Easy"),
        ("medium", "Medium"),
        ("hard", "Hard"),
        ("legendary", "Legendary"),
    ]
    name = models.CharField(max_length=128)
    description = models.TextField()
    criteria = models.JSONField()
    points_reward = models.IntegerField(default=0)
    badge_reward = models.ForeignKey(
        "Badge", null=True, blank=True, on_delete=models.SET_NULL
    )
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    difficulty_level = models.CharField(
        max_length=16, choices=DIFFICULTY_CHOICES, default="easy"
    )


# --- UserQuest Model ---
class UserQuest(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
    progress = models.JSONField(default=dict)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "quest")


# --- Challenge Model ---
class Challenge(BaseModel):
    CHALLENGE_TYPE_CHOICES = [
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
        ("special", "Special"),
    ]
    name = models.CharField(max_length=128)
    description = models.TextField()
    challenge_type = models.CharField(
        max_length=16, choices=CHALLENGE_TYPE_CHOICES, default="daily"
    )
    criteria = models.JSONField()
    points_reward = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    period_duration = models.DurationField(null=True, blank=True)


# --- UserChallenge Model ---
class UserChallenge(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    progress = models.JSONField(default=dict)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    period_start = models.DateTimeField(null=True, blank=True)
    period_end = models.DateTimeField(null=True, blank=True)


# --- Event Model ---
class Event(BaseModel):
    EVENT_TYPE_CHOICES = [
        ("seasonal", "Seasonal"),
        ("special", "Special"),
        ("promotion", "Promotion"),
    ]
    name = models.CharField(max_length=128)
    description = models.TextField()
    event_type = models.CharField(
        max_length=16, choices=EVENT_TYPE_CHOICES, default="special"
    )
    point_multiplier = models.FloatField(default=1.0)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    special_rewards = models.JSONField(default=dict)

    def is_currently_active(self):
        from django.utils import timezone

        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date
