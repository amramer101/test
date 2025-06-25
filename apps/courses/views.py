from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from django.db import transaction
from drf_spectacular.utils import extend_schema
from drf_spectacular.openapi import OpenApiParameter, OpenApiTypes

from .models import (
    Course,
    CourseCategory,
    Section,
    Lesson,
    Enrollment,
    LessonProgress,
    CourseReview,
)
from .serializers import (
    CourseSerializer,
    CourseListSerializer,
    CourseCategorySerializer,
    SectionSerializer,
    LessonSerializer,
    EnrollmentSerializer,
    EnrollmentCreateSerializer,
    LessonProgressSerializer,
    CourseReviewSerializer,
)
from apps.shared.permissions import (
    RoleBasedPermission,
    PermissionRequired,
    DynamicPermissionRequired,
)
from apps.courses.services import (
    CourseService,
    ProgressService,
    EnrollmentService,
)
from apps.gamification.utils import award_points

# --- CourseCategoryViewSet ---


class CourseCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CourseCategory.objects.filter(is_active=True, is_deleted=False)
    serializer_class = CourseCategorySerializer
    permission_classes = [IsAuthenticated]


# --- CourseViewSet ---


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.filter(is_deleted=False)
    serializer_class = CourseSerializer
    permission_classes = [RoleBasedPermission]
    permission_required_map = {
        "list": "view_course",
        "retrieve": "view_course",
        "create": "create_course",
        "update": "manage_courses",
        "partial_update": "manage_courses",
        "destroy": "manage_courses",
        "enroll": "enroll_course",
        "unenroll": "enroll_course",
        "my_courses": "view_course",
        "progress": "view_course",
    }

    def get_serializer_class(self):
        if self.action == "list":
            return CourseListSerializer
        return CourseSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [
                IsAuthenticated(),
                DynamicPermissionRequired(self.permission_required_map[self.action]),
            ]
        return super().get_permissions()

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def enroll(self, request, pk=None):
        course = self.get_object()
        user = request.user
        try:
            enrollment = CourseService.enroll_user(user, course)
            serializer = EnrollmentSerializer(enrollment, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def unenroll(self, request, pk=None):
        course = self.get_object()
        user = request.user
        try:
            EnrollmentService.unenroll_user(user, course)
            return Response(
                {"detail": "Unenrolled successfully."}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def my_courses(self, request):
        enrollments = Enrollment.objects.filter(user=request.user, is_deleted=False)
        serializer = EnrollmentSerializer(
            enrollments, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def progress(self, request, pk=None):
        course = self.get_object()
        enrollment = Enrollment.objects.filter(
            user=request.user, course=course, is_deleted=False
        ).first()
        if not enrollment:
            return Response(
                {"detail": "Not enrolled in this course."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = EnrollmentSerializer(enrollment, context={"request": request})
        return Response(serializer.data)


# --- SectionViewSet ---


class SectionViewSet(viewsets.ModelViewSet):
    serializer_class = SectionSerializer
    permission_classes = [RoleBasedPermission]
    permission_required_map = {
        "list": "view_sections",
        "retrieve": "view_sections",
        "create": "manage_sections",
        "update": "manage_sections",
        "partial_update": "manage_sections",
        "destroy": "manage_sections",
    }

    def get_queryset(self):
        course_id = self.kwargs.get("course_pk")
        return Section.objects.filter(course_id=course_id, is_deleted=False)

    def perform_create(self, serializer):
        course_id = self.kwargs.get("course_pk")
        course = get_object_or_404(Course, pk=course_id)
        serializer.save(course=course)


# --- LessonViewSet ---


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="course_pk", type=OpenApiTypes.UUID, location=OpenApiParameter.PATH
        )
    ]
)
class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    permission_classes = [RoleBasedPermission]
    permission_required_map = {
        "list": "view_lessons",
        "retrieve": "view_lessons",
        "create": "manage_lessons",
        "update": "manage_lessons",
        "partial_update": "manage_lessons",
        "destroy": "manage_lessons",
        "complete": "complete_lessons",
    }

    def get_queryset(self):
        section_id = self.kwargs.get("section_pk")
        return Lesson.objects.filter(section_id=section_id, is_deleted=False)

    def perform_create(self, serializer):
        section_id = self.kwargs.get("section_pk")
        section = get_object_or_404(Section, pk=section_id)
        serializer.save(section=section)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def complete(self, request, section_pk=None, pk=None):
        lesson = self.get_object()
        user = request.user
        try:
            with transaction.atomic():
                progress = ProgressService.complete_lesson(user, lesson)
                serializer = LessonProgressSerializer(
                    progress, context={"request": request}
                )
                return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# --- EnrollmentViewSet ---


class EnrollmentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Enrollment.objects.filter(is_deleted=False)
    serializer_class = EnrollmentSerializer
    permission_classes = [RoleBasedPermission]
    permission_required_map = {
        "list": "view_enrollments",
        "retrieve": "view_enrollments",
        "create": "enroll_course",
        "destroy": "unenroll_course",
    }

    def get_queryset(self):
        # Only allow users to see their own enrollments unless admin
        user = self.request.user
        if user.is_staff:
            return Enrollment.objects.filter(is_deleted=False)
        return Enrollment.objects.filter(user=user, is_deleted=False)

    def get_serializer_class(self):
        if self.action == "create":
            return EnrollmentCreateSerializer
        return EnrollmentSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# --- CourseReviewViewSet ---


class CourseReviewViewSet(viewsets.ModelViewSet):
    queryset = CourseReview.objects.filter(is_deleted=False)
    serializer_class = CourseReviewSerializer
    permission_classes = [RoleBasedPermission]
    permission_required_map = {
        "list": "view_reviews",
        "retrieve": "view_reviews",
        "create": "create_review",
        "update": "manage_reviews",
        "partial_update": "manage_reviews",
        "destroy": "manage_reviews",
    }

    def get_queryset(self):
        # Only published reviews for non-admins
        if self.request.user.is_staff:
            return CourseReview.objects.filter(is_deleted=False)
        return CourseReview.objects.filter(is_published=True, is_deleted=False)

    def perform_create(self, serializer):
        user = self.request.user
        course = serializer.validated_data["course"]
        # Only enrolled users can review, one review per course
        if not Enrollment.objects.filter(
            user=user, course=course, is_deleted=False
        ).exists():
            raise PermissionError("You must be enrolled in the course to review it.")
        if CourseReview.objects.filter(
            user=user, course=course, is_deleted=False
        ).exists():
            raise PermissionError("You have already reviewed this course.")
        serializer.save(user=user)

    def perform_update(self, serializer):
        # Only allow review owner or admin to update
        instance = serializer.instance
        user = self.request.user
        if instance.user != user and not user.is_staff:
            raise PermissionError("You can only update your own reviews.")
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if instance.user != user and not user.is_staff:
            raise PermissionError("You can only delete your own reviews.")
        instance.delete()
