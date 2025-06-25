from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Count, Q

from .models import (
    Course,
    Section,
    Lesson,
    Enrollment,
    LessonProgress,
    CourseReview,
)
from apps.gamification.utils import award_points
from apps.shared.exceptions import BusinessLogicError


class CourseService:
    @staticmethod
    @transaction.atomic
    def enroll_user(user, course):
        if Enrollment.objects.filter(
            user=user, course=course, is_deleted=False
        ).exists():
            raise BusinessLogicError("User is already enrolled in this course.")
        # Optionally check prerequisites
        for prereq in course.prerequisites.all():
            if not Enrollment.objects.filter(
                user=user, course=prereq, status="completed", is_deleted=False
            ).exists():
                raise BusinessLogicError(f"Prerequisite not completed: {prereq.title}")
        enrollment = Enrollment.objects.create(
            user=user, course=course, status="active"
        )
        # Optionally, create LessonProgress records for all lessons
        for section in course.sections.filter(is_published=True, is_deleted=False):
            for lesson in section.lessons.filter(is_published=True, is_deleted=False):
                LessonProgress.objects.get_or_create(
                    enrollment=enrollment, lesson=lesson
                )
        return enrollment

    @staticmethod
    @transaction.atomic
    def unenroll_user(user, course):
        enrollment = Enrollment.objects.filter(
            user=user, course=course, is_deleted=False
        ).first()
        if not enrollment:
            raise BusinessLogicError("User is not enrolled in this course.")
        enrollment.status = "dropped"
        enrollment.save(update_fields=["status"])
        # Optionally, soft-delete lesson progresses
        enrollment.lesson_progresses.update(is_deleted=True)
        return enrollment

    @staticmethod
    def calculate_progress(enrollment):
        total_lessons = Lesson.objects.filter(
            section__course=enrollment.course, is_published=True, is_deleted=False
        ).count()
        completed = LessonProgress.objects.filter(
            enrollment=enrollment, is_completed=True, is_deleted=False
        ).count()
        if total_lessons == 0:
            return 0
        return round((completed / total_lessons) * 100, 2)

    @staticmethod
    def check_completion(enrollment):
        progress = CourseService.calculate_progress(enrollment)
        if progress == 100 and enrollment.status != "completed":
            enrollment.status = "completed"
            enrollment.completed_at = timezone.now()
            enrollment.save(update_fields=["status", "completed_at"])
            # Award course completion points
            award_points(
                user=enrollment.user,
                points=enrollment.course.points_reward,
                action="earn",
                reference_type="course",
                reference_id=str(enrollment.course.id),
                description=f"Completed course: {enrollment.course.title}",
            )
            return True
        return False

    @staticmethod
    def get_recommended_courses(user, limit=5):
        # Simple recommendation: courses not enrolled in, ordered by popularity
        enrolled_ids = Enrollment.objects.filter(
            user=user, is_deleted=False
        ).values_list("course_id", flat=True)
        return (
            Course.objects.filter(is_published=True, is_deleted=False)
            .exclude(id__in=enrolled_ids)
            .annotate(num_enrollments=Count("enrollments"))
            .order_by("-num_enrollments")[:limit]
        )


class ProgressService:
    @staticmethod
    @transaction.atomic
    def complete_lesson(user, lesson):
        # Find enrollment
        enrollment = Enrollment.objects.filter(
            user=user, course=lesson.section.course, is_deleted=False
        ).first()
        if not enrollment:
            raise BusinessLogicError("User is not enrolled in this course.")
        progress, created = LessonProgress.objects.get_or_create(
            enrollment=enrollment, lesson=lesson
        )
        if progress.is_completed:
            raise BusinessLogicError("Lesson already completed.")
        progress.is_completed = True
        progress.completed_at = timezone.now()
        progress.time_spent_minutes += (
            lesson.estimated_minutes
        )  # Optionally track actual time
        progress.attempts_count += 1
        progress.save()
        # Award points for lesson
        award_points(
            user=user,
            points=lesson.points_reward,
            action="earn",
            reference_type="lesson",
            reference_id=str(lesson.id),
            description=f"Completed lesson: {lesson.title}",
        )
        # Update enrollment progress
        enrollment.progress_percentage = CourseService.calculate_progress(enrollment)
        enrollment.save(update_fields=["progress_percentage"])
        # Check for course completion
        CourseService.check_completion(enrollment)
        return progress

    @staticmethod
    def get_course_progress(enrollment):
        lessons = Lesson.objects.filter(
            section__course=enrollment.course, is_published=True, is_deleted=False
        )
        completed = LessonProgress.objects.filter(
            enrollment=enrollment, is_completed=True, is_deleted=False
        ).count()
        total = lessons.count()
        return {
            "total_lessons": total,
            "completed_lessons": completed,
            "progress_percentage": CourseService.calculate_progress(enrollment),
            "status": enrollment.status,
            "completed_at": enrollment.completed_at,
        }

    @staticmethod
    def calculate_estimated_completion(enrollment):
        # Estimate based on average pace
        completed = LessonProgress.objects.filter(
            enrollment=enrollment, is_completed=True, is_deleted=False
        ).count()
        total = Lesson.objects.filter(
            section__course=enrollment.course, is_published=True, is_deleted=False
        ).count()
        if completed == 0:
            return None
        days = (timezone.now().date() - enrollment.enrolled_at.date()).days or 1
        avg_per_day = completed / days
        remaining = total - completed
        if avg_per_day == 0:
            return None
        estimated_days = int(remaining / avg_per_day)
        return timezone.now().date() + timezone.timedelta(days=estimated_days)


class EnrollmentService:
    @staticmethod
    def enroll_user(user, course):
        return CourseService.enroll_user(user, course)

    @staticmethod
    def unenroll_user(user, course):
        return CourseService.unenroll_user(user, course)

    @staticmethod
    def validate_capacity(course):
        # Placeholder for capacity logic
        return True

    @staticmethod
    def verify_prerequisites(user, course):
        for prereq in course.prerequisites.all():
            if not Enrollment.objects.filter(
                user=user, course=prereq, status="completed", is_deleted=False
            ).exists():
                raise BusinessLogicError(f"Prerequisite not completed: {prereq.title}")
        return True
