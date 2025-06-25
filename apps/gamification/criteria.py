from abc import ABC, abstractmethod


class CriteriaEvaluator(ABC):
    @abstractmethod
    def evaluate(self, user, profile, criteria_data):
        pass


class PointsCriteriaEvaluator(CriteriaEvaluator):
    def evaluate(self, user, profile, criteria_data):
        min_points = criteria_data.get("min_points", 0)
        return profile.total_points >= min_points


class ActionsCriteriaEvaluator(CriteriaEvaluator):
    def evaluate(self, user, profile, criteria_data):
        # Example: {'action': 'complete_lesson', 'count': 10}
        from apps.gamification.models import PointActivity

        action = criteria_data.get("action")
        count = criteria_data.get("count", 1)
        return PointActivity.objects.filter(user=user, action=action).count() >= count


class StreakCriteriaEvaluator(CriteriaEvaluator):
    def evaluate(self, user, profile, criteria_data):
        from apps.gamification.models import Streak

        streak_type = criteria_data.get("streak_type", "login")
        min_streak = criteria_data.get("min_streak", 1)
        streak = Streak.objects.filter(user=user, streak_type=streak_type).first()
        return streak and streak.current_count >= min_streak


class QuestCriteriaEvaluator(CriteriaEvaluator):
    def evaluate(self, user, profile, criteria_data):
        from apps.gamification.models import UserQuest

        quest_id = criteria_data.get("quest_id")
        return UserQuest.objects.filter(
            user=user, quest_id=quest_id, is_completed=True
        ).exists()


class SpendingCriteriaEvaluator(CriteriaEvaluator):
    def evaluate(self, user, profile, criteria_data):
        from apps.gamification.models import PointLedger

        min_spent = criteria_data.get("min_spent", 0)
        spent = (
            PointLedger.objects.filter(user=user, transaction_type="spend").aggregate(
                total=models.Sum("points")
            )["total"]
            or 0
        )
        return abs(spent) >= min_spent


class SocialCriteriaEvaluator(CriteriaEvaluator):
    def evaluate(self, user, profile, criteria_data):
        # Example: {'reviews': 5, 'helpful_votes': 10}
        from apps.courses.models import CourseReview

        reviews = criteria_data.get("reviews", 0)
        return (
            CourseReview.objects.filter(user=user, is_published=True).count() >= reviews
        )


class LevelCriteriaEvaluator(CriteriaEvaluator):
    def evaluate(self, user, profile, criteria_data):
        min_level = criteria_data.get("min_level", 1)
        return profile.current_level and profile.current_level.number >= min_level


class TimeCriteriaEvaluator(CriteriaEvaluator):
    def evaluate(self, user, profile, criteria_data):
        from django.utils import timezone

        min_days = criteria_data.get("min_days", 0)
        if hasattr(user, "date_joined"):
            days = (timezone.now().date() - user.date_joined.date()).days
            return days >= min_days
        return False


class CriteriaRegistry:
    _registry = {}

    @classmethod
    def register_evaluator(cls, key, evaluator):
        cls._registry[key] = evaluator

    @classmethod
    def evaluate_criteria(cls, user, profile, criteria):
        # criteria: dict, e.g. {'points': {...}, 'streak': {...}}
        for key, data in criteria.items():
            evaluator = cls._registry.get(key)
            if evaluator and not evaluator.evaluate(user, profile, data):
                return False
        return True


# Register evaluators
CriteriaRegistry.register_evaluator("points", PointsCriteriaEvaluator())
CriteriaRegistry.register_evaluator("actions", ActionsCriteriaEvaluator())
CriteriaRegistry.register_evaluator("streak", StreakCriteriaEvaluator())
CriteriaRegistry.register_evaluator("quest", QuestCriteriaEvaluator())
CriteriaRegistry.register_evaluator("spending", SpendingCriteriaEvaluator())
CriteriaRegistry.register_evaluator("social", SocialCriteriaEvaluator())
CriteriaRegistry.register_evaluator("level", LevelCriteriaEvaluator())
CriteriaRegistry.register_evaluator("time", TimeCriteriaEvaluator())
