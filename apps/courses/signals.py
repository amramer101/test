from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.db.models import Count

from apps.courses.models import LessonProgress, Enrollment, CourseReview
from apps.gamification.utils import award_points, check_and_award_badges
from apps.gamification.models import UserPointProfile
from apps.shared.exceptions import BusinessLogicError

# --- Lesson Completion Signal ---


@receiver(post_save, sender=LessonProgress)
def handle_lesson_completion(sender, instance, created, **kwargs):
    """
    Award points when a lesson is completed and check for course completion.
    """
    if instance.is_completed and instance.completed_at and created is False:
        lesson = instance.lesson
        user = instance.enrollment.user
        try:
            # Award lesson points
            award_points(
                user=user,
                points=lesson.points_reward,
                action=f"Completed lesson: {lesson.title}",
                reference_type="lesson",
                reference_id=str(lesson.id),
            )
            # Check for course completion
            enrollment = instance.enrollment
            total_lessons = (
                lesson.section.course.sections.filter(is_published=True)
                .prefetch_related("lessons")
                .aggregate(total=Count("lessons"))["total"]
            )
            completed_lessons = LessonProgress.objects.filter(
                enrollment=enrollment, is_completed=True
            ).count()
            if total_lessons and completed_lessons == total_lessons:
                # Mark enrollment as completed
                enrollment.status = "completed"
                enrollment.completed_at = timezone.now()
                enrollment.save(update_fields=["status", "completed_at"])
                # Award course completion bonus
                course = lesson.section.course
                award_points(
                    user=user,
                    points=course.points_reward,
                    action=f"Completed course: {course.title}",
                    reference_type="course",
                    reference_id=str(course.id),
                )
                # Check for badges
                check_and_award_badges(user)
        except Exception as e:
            # Prevent signal failure from breaking core logic
            pass


# --- Enrollment Signal ---


@receiver(post_save, sender=Enrollment)
def handle_enrollment(sender, instance, created, **kwargs):
    """
    Award welcome points for first enrollment or enrollment milestones.
    """
    if created:
        user = instance.user
        try:
            total_enrollments = Enrollment.objects.filter(user=user).count()
            if total_enrollments == 1:
                # First course enrollment bonus
                award_points(
                    user=user,
                    points=10,
                    action="First course enrollment",
                    reference_type="enrollment",
                    reference_id=str(instance.id),
                )
            elif total_enrollments in [5, 10, 25, 50]:
                # Milestone bonus
                award_points(
                    user=user,
                    points=total_enrollments * 2,
                    action=f"Enrollment milestone: {total_enrollments} courses",
                    reference_type="enrollment",
                    reference_id=str(instance.id),
                )
        except Exception:
            pass


# --- Course Review Signal ---


@receiver(post_save, sender=CourseReview)
def handle_course_review(sender, instance, created, **kwargs):
    """
    Award points for leaving a course review.
    """
    if created and instance.is_published:
        user = instance.user
        try:
            award_points(
                user=user,
                points=5,
                action=f"Left a review for course: {instance.course.title}",
                reference_type="review",
                reference_id=str(instance.id),
            )
        except Exception:
            pass


# --- Review Deletion Signal (Optional: Remove points if review is deleted) ---


@receiver(post_delete, sender=CourseReview)
def handle_course_review_delete(sender, instance, **kwargs):
    """
    Optionally, deduct points if a review is deleted.
    """
    # This is optional and can be customized as needed.
    pass
