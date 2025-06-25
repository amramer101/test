from rest_framework import serializers
from rest_framework.fields import empty
from django.contrib.auth import get_user_model
from django.utils import timezone


class BaseSerializer(serializers.ModelSerializer):
    """
    Base serializer with common functionality for all domain serializers.
    """

    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        """Override create to add audit fields if available."""
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            if hasattr(self.Meta.model, "created_by"):
                validated_data["created_by"] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Override update to add audit fields if available."""
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            if hasattr(instance, "updated_by"):
                validated_data["updated_by"] = request.user
        return super().update(instance, validated_data)


class AuditableSerializer(BaseSerializer):
    """
    Serializer for models that include audit fields (created_by, updated_by).
    """

    created_by = serializers.StringRelatedField(read_only=True)
    updated_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        fields = BaseSerializer.Meta.fields + ["created_by", "updated_by"]


class SoftDeleteSerializer(AuditableSerializer):
    """
    Serializer for models that support soft delete functionality.
    """

    is_deleted = serializers.BooleanField(read_only=True)
    deleted_at = serializers.DateTimeField(read_only=True)
    deleted_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        fields = AuditableSerializer.Meta.fields + [
            "is_deleted",
            "deleted_at",
            "deleted_by",
        ]


class DynamicFieldsSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional 'fields' argument to
    control which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop("fields", None)
        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class TimestampField(serializers.Field):
    """
    Custom field for handling Unix timestamps.
    """

    def to_representation(self, value):
        if value is None:
            return None
        return int(value.timestamp())

    def to_internal_value(self, data):
        if data is None:
            return None
        try:
            return timezone.datetime.fromtimestamp(int(data), tz=timezone.utc)
        except (ValueError, TypeError):
            raise serializers.ValidationError("Invalid timestamp format.")


class BulkSerializerMixin:
    """
    Mixin to support bulk operations in serializers.
    """

    def to_internal_value(self, data):
        if isinstance(data, list):
            return [super().to_internal_value(item) for item in data]
        return super().to_internal_value(data)

    def create(self, validated_data):
        if isinstance(validated_data, list):
            return [self.Meta.model.objects.create(**item) for item in validated_data]
        return super().create(validated_data)


class PasswordValidationMixin:
    """
    Mixin to add password validation to serializers.
    """

    def validate_password(self, value):
        """
        Validate password strength.
        """
        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long."
            )

        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError(
                "Password must contain at least one digit."
            )

        if not any(char.isupper() for char in value):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter."
            )

        if not any(char.islower() for char in value):
            raise serializers.ValidationError(
                "Password must contain at least one lowercase letter."
            )

        if not any(char in "!@#$%^&*()_+-=[]{}|;:,.<>?" for char in value):
            raise serializers.ValidationError(
                "Password must contain at least one special character."
            )

        return value


class StandardResultSerializer(serializers.Serializer):
    """
    Standardized response format for API endpoints.
    """

    success = serializers.BooleanField(default=True)
    message = serializers.CharField(max_length=255, required=False)
    data = serializers.JSONField(required=False)
    errors = serializers.JSONField(required=False)
    meta = serializers.JSONField(required=False)

    def to_representation(self, instance):
        """
        Convert the response to standard format.
        """
        if isinstance(instance, dict):
            return instance

        return {
            "success": True,
            "data": instance,
            "message": getattr(instance, "message", None),
            "meta": getattr(instance, "meta", None),
        }


class ErrorSerializer(serializers.Serializer):
    """
    Standardized error response format.
    """

    success = serializers.BooleanField(default=False)
    message = serializers.CharField(max_length=255)
    errors = serializers.JSONField(required=False)
    error_code = serializers.CharField(max_length=50, required=False)
    timestamp = serializers.DateTimeField(default=timezone.now)


class PaginatedResponseSerializer(serializers.Serializer):
    """
    Serializer for paginated responses.
    """

    count = serializers.IntegerField()
    next = serializers.URLField(allow_null=True)
    previous = serializers.URLField(allow_null=True)
    results = serializers.ListField()


class ChoicesSerializer(serializers.Serializer):
    """
    Serializer for returning choice field options.
    """

    value = serializers.CharField()
    label = serializers.CharField()

    @classmethod
    def get_choices_data(cls, choices):
        """
        Convert Django choices to serializer format.
        """
        return [{"value": choice[0], "label": choice[1]} for choice in choices]
