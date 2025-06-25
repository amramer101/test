from rest_framework import serializers
from django.db.models import Avg, Count
from django.utils import timezone
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.openapi import OpenApiTypes

from apps.courses.models import (
    Course,
    CourseCategory,
    Section,
    Lesson,
    Enrollment,
    LessonProgress,
    CourseReview,
)
from apps.shared.serializers import (
    BaseSerializer,
    AuditableSerializer,
    DynamicFieldsSerializer,
)
from apps.authentication.models import User

# --- Category ---


class CourseCategorySerializer(BaseSerializer):
    class Meta:
        model = CourseCategory
        fields = ["id", "name", "description", "is_active", "created_at", "updated_at"]


# --- Course ---


class CourseListSerializer(DynamicFieldsSerializer, serializers.ModelSerializer):
    instructor_name = serializers.CharField(
        source="instructor.get_full_name", read_only=True
    )
    enrollment_count = serializers.IntegerField(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "description",
            "difficulty_level",
            "points_reward",
            "thumbnail_image",
            "instructor_name",
            "enrollment_count",
            "average_rating",
            "category_name",
        ]


class InstructorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email"]


class CourseSerializer(DynamicFieldsSerializer, serializers.ModelSerializer):
    instructor = InstructorSerializer(read_only=True)
    category = CourseCategorySerializer(read_only=True)
    enrollment_count = serializers.SerializerMethodField()
    completion_rate = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    is_enrolled = serializers.SerializerMethodField()
    prerequisites = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "description",
            "difficulty_level",
            "estimated_hours",
            "points_reward",
            "is_published",
            "instructor",
            "category",
            "prerequisites",
            "thumbnail_image",
            "enrollment_count",
            "completion_rate",
            "average_rating",
            "is_enrolled",
            "created_at",
            "updated_at",
        ]

    @extend_schema_field(OpenApiTypes.INT)
    def get_enrollment_count(self, obj):
        return obj.enrollment_count

    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_completion_rate(self, obj):
        return obj.completion_rate

    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_average_rating(self, obj):
        return obj.average_rating

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_is_enrolled(self, obj):
        user = self.context.get("request").user if self.context.get("request") else None
        if user and user.is_authenticated:
            return Enrollment.objects.filter(
                user=user, course=obj, is_deleted=False
            ).exists()
        return False

    def validate_points_reward(self, value):
        if value < 0:
            raise serializers.ValidationError("Points reward must be positive.")
        return value


# --- Section ---


class LessonListSerializer(DynamicFieldsSerializer, serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            "id",
            "title",
            "content_type",
            "order_index",
            "estimated_minutes",
            "points_reward",
            "is_published",
        ]


class SectionSerializer(DynamicFieldsSerializer, serializers.ModelSerializer):
    lessons = LessonListSerializer(many=True, read_only=True)
    lesson_count = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = [
            "id",
            "course",
            "title",
            "description",
            "order_index",
            "is_published",
            "lessons",
            "lesson_count",
        ]

    @extend_schema_field(OpenApiTypes.INT)
    def get_lesson_count(self, obj):
        return obj.lessons.count()


# --- Lesson ---


class LessonSerializer(DynamicFieldsSerializer, serializers.ModelSerializer):
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            "id",
            "section",
            "title",
            "content_type",
            "content_data",
            "order_index",
            "estimated_minutes",
            "points_reward",
            "is_published",
            "progress",
        ]

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_progress(self, obj):
        user = self.context.get("request").user if self.context.get("request") else None
        if not user or not user.is_authenticated:
            return None
        enrollment = Enrollment.objects.filter(
            user=user, course=obj.section.course, is_deleted=False
        ).first()
        if not enrollment:
            return None
        progress = LessonProgress.objects.filter(
            enrollment=enrollment, lesson=obj
        ).first()
        if not progress:
            return None
        return {
            "is_completed": progress.is_completed,
            "started_at": progress.started_at,
            "completed_at": progress.completed_at,
            "time_spent_minutes": progress.time_spent_minutes,
            "attempts_count": progress.attempts_count,
        }

    def validate_content_data(self, value):
        content_type = self.initial_data.get("content_type")
        if content_type == "video" and "url" not in value:
            raise serializers.ValidationError(
                "Video lessons must include a 'url' in content_data."
            )
        if content_type == "quiz" and "questions" not in value:
            raise serializers.ValidationError(
                "Quiz lessons must include 'questions' in content_data."
            )
        return value


# --- Enrollment ---


class CourseSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id", "title", "thumbnail_image", "points_reward"]


class EnrollmentSerializer(DynamicFieldsSerializer, serializers.ModelSerializer):
    course = CourseSummarySerializer(read_only=True)
    lessons_completed = serializers.SerializerMethodField()
    estimated_completion_date = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = [
            "id",
            "user",
            "course",
            "enrolled_at",
            "status",
            "progress_percentage",
            "completed_at",
            "certificate_issued",
            "lessons_completed",
            "estimated_completion_date",
        ]

    @extend_schema_field(OpenApiTypes.INT)
    def get_lessons_completed(self, obj):
        return LessonProgress.objects.filter(enrollment=obj, is_completed=True).count()

    @extend_schema_field(OpenApiTypes.DATE)
    def get_estimated_completion_date(self, obj):
        # Simple estimation: based on average pace
        total_lessons = Lesson.objects.filter(
            section__course=obj.course, is_published=True
        ).count()
        completed = LessonProgress.objects.filter(
            enrollment=obj, is_completed=True
        ).count()
        if completed == 0:
            return None
        days = (timezone.now().date() - obj.enrolled_at.date()).days or 1
        avg_per_day = completed / days
        remaining = total_lessons - completed
        if avg_per_day == 0:
            return None
        estimated_days = int(remaining / avg_per_day)
        return (timezone.now() + timezone.timedelta(days=estimated_days)).date()


class EnrollmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ["course"]

    def validate(self, data):
        user = self.context["request"].user
        course = data["course"]
        if Enrollment.objects.filter(
            user=user, course=course, is_deleted=False
        ).exists():
            raise serializers.ValidationError(
                "You are already enrolled in this course."
            )
        # Optionally check prerequisites here
        return data


# --- Lesson Progress ---


class LessonProgressSerializer(DynamicFieldsSerializer, serializers.ModelSerializer):
    lesson = LessonListSerializer(read_only=True)

    class Meta:
        model = LessonProgress
        fields = [
            "id",
            "enrollment",
            "lesson",
            "started_at",
            "completed_at",
            "time_spent_minutes",
            "attempts_count",
            "is_completed",
        ]


# --- Course Review ---


class ReviewUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name"]


class CourseReviewSerializer(DynamicFieldsSerializer, serializers.ModelSerializer):
    user = ReviewUserSerializer(read_only=True)
    helpful_votes = serializers.IntegerField(read_only=True)

    class Meta:
        model = CourseReview
        fields = [
            "id",
            "user",
            "course",
            "rating",
            "review_text",
            "is_published",
            "helpful_votes",
            "created_at",
        ]

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
