from django.db import models
from django.conf import settings
from apps.shared.models import BaseModel
from django.core.validators import MinValueValidator, MaxValueValidator


class CourseCategory(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Course Categories"
        ordering = ["name"]


class Course(BaseModel):
    DIFFICULTY_CHOICES = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    ]
    title = models.CharField(max_length=255)
    description = models.TextField()
    difficulty_level = models.CharField(
        max_length=20, choices=DIFFICULTY_CHOICES, default="beginner"
    )
    estimated_hours = models.PositiveIntegerField(default=0)
    points_reward = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=False)
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="courses_taught",
    )
    category = models.ForeignKey(
        CourseCategory, on_delete=models.SET_NULL, null=True, related_name="courses"
    )
    prerequisites = models.ManyToManyField(
        "self", symmetrical=False, blank=True, related_name="postrequisites"
    )
    thumbnail_image = models.ImageField(
        upload_to="course_thumbnails/", blank=True, null=True
    )

    def __str__(self):
        return self.title

    @property
    def enrollment_count(self):
        return self.enrollments.count()

    @property
    def completion_rate(self):
        total_enrollments = self.enrollment_count
        if total_enrollments == 0:
            return 0.0
        completed_enrollments = self.enrollments.filter(status="completed").count()
        return (completed_enrollments / total_enrollments) * 100

    @property
    def average_rating(self):
        return self.reviews.aggregate(models.Avg("rating"))["rating__avg"] or 0.0

    class Meta:
        ordering = ["-created_at"]


class Section(BaseModel):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="sections"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    order_index = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.course.title} - Section {self.order_index}: {self.title}"

    class Meta:
        ordering = ["order_index"]
        unique_together = ("course", "order_index")


class Lesson(BaseModel):
    CONTENT_TYPE_CHOICES = [
        ("video", "Video"),
        ("text", "Text"),
        ("quiz", "Quiz"),
        ("assignment", "Assignment"),
    ]
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name="lessons"
    )
    title = models.CharField(max_length=255)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES)
    content_data = models.JSONField(default=dict)
    order_index = models.PositiveIntegerField(default=0)
    estimated_minutes = models.PositiveIntegerField(default=0)
    points_reward = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.section.title} - Lesson {self.order_index}: {self.title}"

    class Meta:
        ordering = ["order_index"]
        unique_together = ("section", "order_index")


class Enrollment(BaseModel):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("completed", "Completed"),
        ("dropped", "Dropped"),
        ("suspended", "Suspended"),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="enrollments"
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    progress_percentage = models.FloatField(
        default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    certificate_issued = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email} enrolled in {self.course.title}"

    class Meta:
        unique_together = ("user", "course")


class LessonProgress(BaseModel):
    enrollment = models.ForeignKey(
        Enrollment, on_delete=models.CASCADE, related_name="lesson_progress"
    )
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name="progress"
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_spent_minutes = models.PositiveIntegerField(default=0)
    attempts_count = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Progress for {self.enrollment.user.email} on {self.lesson.title}"

    class Meta:
        unique_together = ("enrollment", "lesson")
        verbose_name_plural = "Lesson Progress"


class CourseReview(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews"
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    review_text = models.TextField()
    is_published = models.BooleanField(default=True)
    helpful_votes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Review for {self.course.title} by {self.user.email}"

    class Meta:
        unique_together = ("user", "course")
        ordering = ["-created_at"]
