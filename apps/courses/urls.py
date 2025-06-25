from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedSimpleRouter
from django.urls import path, include
from .views import (
    CourseViewSet,
    CourseCategoryViewSet,
    SectionViewSet,
    LessonViewSet,
    EnrollmentViewSet,
    CourseReviewViewSet,
)

app_name = "courses"

# Main router
router = DefaultRouter()
router.register(r"categories", CourseCategoryViewSet, basename="course-category")
router.register(r"courses", CourseViewSet, basename="course")
router.register(r"enrollments", EnrollmentViewSet, basename="enrollment")
router.register(r"reviews", CourseReviewViewSet, basename="review")

# Nested routers for sections under courses
courses_router = NestedSimpleRouter(router, r"courses", lookup="course")
courses_router.register(r"sections", SectionViewSet, basename="course-sections")

# Nested routers for lessons under sections
sections_router = NestedSimpleRouter(courses_router, r"sections", lookup="section")
sections_router.register(r"lessons", LessonViewSet, basename="section-lessons")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(courses_router.urls)),
    path("", include(sections_router.urls)),
]
