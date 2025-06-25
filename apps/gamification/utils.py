from .models import (
    UserPointProfile,
    PointActivity,
    Badge,
    UserBadge,
    Level,
    PointLedger,
    Streak,
    Quest,
    UserQuest,
    Challenge,
    UserChallenge,
    Event,
)
from .criteria import CriteriaRegistry
from django.db import transaction, models
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist


def award_points(
    user, points, action, description="", reference_type=None, reference_id=None
):
    with transaction.atomic():
        profile, _ = UserPointProfile.objects.get_or_create(user=user)
        profile.total_points += points
        profile.available_points += points
        # Level up logic
        next_level = (
            Level.objects.filter(required_points__gt=profile.total_points)
            .order_by("required_points")
            .first()
        )
        current_level = (
            Level.objects.filter(required_points__lte=profile.total_points)
            .order_by("-required_points")
            .first()
        )
        profile.current_level = current_level
        if current_level and next_level:
            profile.progress_to_next_level = (
                profile.total_points - current_level.required_points
            ) / (next_level.required_points - current_level.required_points)
        else:
            profile.progress_to_next_level = 1.0
        profile.save()
        PointActivity.objects.create(
            user=user,
            action=action,
            points=points,
            transaction_type="earn",
            reference_type=reference_type or "",
            reference_id=reference_id or "",
            description=description,
            timestamp=timezone.now(),
        )
        # Ledger entry
        last_ledger = (
            PointLedger.objects.filter(user=user).order_by("-created_at").first()
        )
        balance_after = (last_ledger.balance_after if last_ledger else 0) + points
        PointLedger.objects.create(
            user=user,
            transaction_type="earn",
            points=points,
            balance_after=balance_after,
            reference_type=reference_type or "",
            reference_id=reference_id or "",
            description=description,
        )
        check_and_award_badges(user)


def spend_points(user, amount, reference_type=None, reference_id=None, description=""):
    with transaction.atomic():
        profile = UserPointProfile.objects.get(user=user)
        if profile.available_points < amount:
            raise Exception("Insufficient points.")
        profile.available_points -= amount
        profile.save(update_fields=["available_points"])
        PointActivity.objects.create(
            user=user,
            action="spend_points",
            points=-amount,
            transaction_type="spend",
            reference_type=reference_type or "",
            reference_id=reference_id or "",
            description=description,
            timestamp=timezone.now(),
        )
        last_ledger = (
            PointLedger.objects.filter(user=user).order_by("-created_at").first()
        )
        balance_after = (last_ledger.balance_after if last_ledger else 0) - amount
        PointLedger.objects.create(
            user=user,
            transaction_type="spend",
            points=-amount,
            balance_after=balance_after,
            reference_type=reference_type or "",
            reference_id=reference_id or "",
            description=description,
        )
        return balance_after


def get_user_balance(user):
    profile = UserPointProfile.objects.get(user=user)
    return profile.available_points


def validate_sufficient_points(user, amount):
    profile = UserPointProfile.objects.get(user=user)
    if profile.available_points < amount:
        raise Exception("Insufficient points.")
    return True


def recalculate_user_balance(user):
    last_ledger = PointLedger.objects.filter(user=user).order_by("-created_at").first()
    balance = last_ledger.balance_after if last_ledger else 0
    profile = UserPointProfile.objects.get(user=user)
    profile.available_points = balance
    profile.save(update_fields=["available_points"])
    return balance


def check_and_award_badges(user, **kwargs):
    profile = UserPointProfile.objects.get(user=user)
    badges = Badge.objects.all()
    for badge in badges:
        if not UserBadge.objects.filter(user=user, badge=badge).exists():
            if CriteriaRegistry.evaluate_criteria(user, profile, badge.criteria or {}):
                UserBadge.objects.create(user=user, badge=badge)
    # Spending-based badges example
    total_spent = (
        PointLedger.objects.filter(user=user, transaction_type="spend").aggregate(
            models.Sum("points")
        )["points__sum"]
        or 0
    )
    # Example: if total_spent <= -1000: award "Big Spender" badge
    # ...


def badge_criteria_met(badge, profile):
    # Deprecated: replaced by CriteriaRegistry
    return CriteriaRegistry.evaluate_criteria(
        profile.user, profile, badge.criteria or {}
    )


# --- Streak Management ---
def update_user_streak(user, streak_type):
    """Update or increment a user's streak of the given type."""
    try:
        streak, created = Streak.objects.get_or_create(
            user=user, streak_type=streak_type
        )
        today = timezone.now().date()
        if streak.last_activity_date == today:
            return streak  # Already updated today
        if streak.last_activity_date == today - timezone.timedelta(days=1):
            streak.current_count += 1
        else:
            streak.current_count = 1
        streak.last_activity_date = today
        if streak.current_count > streak.longest_count:
            streak.longest_count = streak.current_count
        streak.is_active = True
        streak.save()
        return streak
    except Exception:
        return None


def reset_user_streak(user, streak_type):
    """Reset a user's streak of the given type."""
    try:
        streak = Streak.objects.get(user=user, streak_type=streak_type)
        streak.current_count = 0
        streak.is_active = False
        streak.save()
    except Streak.DoesNotExist:
        pass


def get_user_streak(user, streak_type):
    """Get a user's streak info for the given type."""
    try:
        return Streak.objects.get(user=user, streak_type=streak_type)
    except Streak.DoesNotExist:
        return None


def check_streak_eligibility(user):
    """Check if user qualifies for streak-based rewards."""
    # Example: award badge for 7-day login streak
    streak = get_user_streak(user, "login")
    if streak and streak.current_count >= 7:
        check_and_award_badges(user)


# --- Quest Management ---
def check_quest_progress(user, quest):
    """Evaluate user progress toward quest completion."""
    try:
        user_quest = UserQuest.objects.get(user=user, quest=quest)
        # Implement logic based on quest.criteria and user activity
        # Placeholder: return user_quest.progress
        return user_quest.progress
    except UserQuest.DoesNotExist:
        return {}


def complete_quest(user, quest):
    """Mark quest as completed and award rewards."""
    try:
        user_quest = UserQuest.objects.get(user=user, quest=quest)
        if not user_quest.is_completed:
            user_quest.is_completed = True
            user_quest.completed_at = timezone.now()
            user_quest.save()
            if quest.points_reward:
                award_points(
                    user, quest.points_reward, f"Completed quest: {quest.name}"
                )
            if quest.badge_reward:
                UserBadge.objects.get_or_create(user=user, badge=quest.badge_reward)
    except UserQuest.DoesNotExist:
        pass


def get_available_quests(user):
    """Get quests user can start based on level/prerequisites."""
    # Placeholder: return all active quests not yet started
    started_quests = UserQuest.objects.filter(user=user).values_list(
        "quest_id", flat=True
    )
    return Quest.objects.filter(is_active=True).exclude(id__in=started_quests)


def update_quest_progress(user, action_type, **context):
    """Update quest progress when user performs actions."""
    # Placeholder: update progress for all active user quests
    active_quests = UserQuest.objects.filter(user=user, is_completed=False)
    for user_quest in active_quests:
        # Implement logic to update progress based on action_type and context
        pass


# --- Challenge Management ---
def get_active_challenges(user, period_type):
    """Get challenges for current period."""
    now = timezone.now()
    return Challenge.objects.filter(is_active=True, period_duration=period_type)


def update_challenge_progress(user, challenge, progress_data):
    """Update challenge progress for a user."""
    try:
        user_challenge, _ = UserChallenge.objects.get_or_create(
            user=user, challenge=challenge
        )
        # Update progress_data as needed
        user_challenge.progress = progress_data
        user_challenge.save()
    except Exception:
        pass


def complete_challenge(user, challenge):
    """Mark challenge completed and award points."""
    try:
        user_challenge = UserChallenge.objects.get(user=user, challenge=challenge)
        if not user_challenge.is_completed:
            user_challenge.is_completed = True
            user_challenge.completed_at = timezone.now()
            user_challenge.save()
            if challenge.points_reward:
                award_points(
                    user,
                    challenge.points_reward,
                    f"Completed challenge: {challenge.name}",
                )
    except UserChallenge.DoesNotExist:
        pass


# --- Event Management ---
def get_active_events():
    """Get currently active time-limited events."""
    now = timezone.now()
    return Event.objects.filter(is_active=True, start_date__lte=now, end_date__gte=now)


def apply_event_multiplier(points, event_type):
    """Apply point multipliers during events."""
    events = Event.objects.filter(event_type=event_type, is_active=True)
    multiplier = 1.0
    for event in events:
        multiplier *= event.point_multiplier
    return int(points * multiplier)


def check_event_eligibility(user, event):
    """Check if user can participate in event."""
    now = timezone.now()
    return event.is_active and event.start_date <= now <= event.end_date


# --- Social Interaction ---
def award_social_points(user, action_type, target_object):
    """Award points for social actions."""
    # Example: award points for comment, like, share, etc.
    points_map = {
        "comment": 3,
        "like": 1,
        "share": 5,
        "referral": 10,
        "discussion": 10,
        "solution": 5,
        "follower": 3,
    }
    points = points_map.get(action_type, 0)
    if points > 0:
        award_points(user, points, f"Social action: {action_type}")


def update_referral_progress(referrer, referred_user):
    """Track referral completions and award points."""
    # Placeholder: implement referral logic
    award_social_points(referrer, "referral", referred_user)
