from django.contrib import admin
from .models import (
    CourseCategory,
    Course,
    Section,
    Lesson,
    Enrollment,
    LessonProgress,
    CourseReview,
)


class SectionInline(admin.TabularInline):
    model = Section
    extra = 1
    fields = ("title", "order_index", "is_published")
    show_change_link = True


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ("title", "content_type", "order_index", "points_reward", "is_published")
    show_change_link = True


@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    search_fields = ("name",)
    list_filter = ("is_active",)
    ordering = ("name",)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "instructor",
        "category",
        "difficulty_level",
        "is_published",
        "enrollment_count",
        "average_rating",
        "created_at",
    )
    list_filter = ("category", "difficulty_level", "is_published")
    search_fields = ("title", "description", "instructor__username")
    readonly_fields = ("enrollment_count", "completion_rate", "average_rating")
    inlines = [SectionInline]
    fieldsets = (
        (
            None,
            {
                "fields": (
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
                )
            },
        ),
        (
            "Statistics",
            {
                "fields": ("enrollment_count", "completion_rate", "average_rating"),
                "classes": ("collapse",),
            },
        ),
        (
            "Audit",
            {
                "fields": ("created_at", "updated_at", "is_deleted"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order_index", "is_published")
    list_filter = ("course", "is_published")
    search_fields = ("title", "course__title")
    ordering = ("course", "order_index")
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "section",
        "content_type",
        "order_index",
        "points_reward",
        "estimated_minutes",
        "is_published",
    )
    list_filter = ("content_type", "is_published", "section__course")
    search_fields = ("title", "section__title", "section__course__title")
    ordering = ("section", "order_index")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "course",
        "status",
        "progress_percentage",
        "enrolled_at",
        "completed_at",
        "certificate_issued",
    )
    list_filter = ("status", "certificate_issued", "enrolled_at")
    search_fields = ("user__username", "course__title")
    readonly_fields = ("progress_percentage", "completed_at")
    ordering = ("-enrolled_at",)


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = (
        "enrollment",
        "lesson",
        "is_completed",
        "started_at",
        "completed_at",
        "time_spent_minutes",
        "attempts_count",
    )
    list_filter = ("is_completed", "lesson__section__course")
    search_fields = ("enrollment__user__username", "lesson__title")
    ordering = ("-started_at",)


@admin.register(CourseReview)
class CourseReviewAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "course",
        "rating",
        "is_published",
        "helpful_votes",
        "created_at",
    )
    list_filter = ("is_published", "rating", "course")
    search_fields = ("user__username", "course__title", "review_text")
    ordering = ("-created_at",)
    actions = ["publish_reviews", "unpublish_reviews"]

    def publish_reviews(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(request, f"{updated} review(s) published.")

    publish_reviews.short_description = "Publish selected reviews"

    def unpublish_reviews(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f"{updated} review(s) unpublished.")

    unpublish_reviews.short_description = "Unpublish selected reviews"
