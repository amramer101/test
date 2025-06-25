import re
import uuid
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model


class PasswordStrengthValidator:
    """
    Validates password strength with customizable requirements.
    """

    def __init__(
        self,
        min_length=8,
        require_uppercase=True,
        require_lowercase=True,
        require_digit=True,
        require_special=True,
    ):
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digit = require_digit
        self.require_special = require_special
        self.special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"

    def __call__(self, value):
        errors = []

        if len(value) < self.min_length:
            errors.append(
                f"Password must be at least {self.min_length} characters long."
            )

        if self.require_uppercase and not any(char.isupper() for char in value):
            errors.append("Password must contain at least one uppercase letter.")

        if self.require_lowercase and not any(char.islower() for char in value):
            errors.append("Password must contain at least one lowercase letter.")

        if self.require_digit and not any(char.isdigit() for char in value):
            errors.append("Password must contain at least one digit.")

        if self.require_special and not any(
            char in self.special_chars for char in value
        ):
            errors.append("Password must contain at least one special character.")

        if errors:
            raise ValidationError(errors)

        return value


class EmailDomainValidator:
    """
    Validates email domains against allowed/blocked lists.
    """

    def __init__(self, allowed_domains=None, blocked_domains=None):
        self.allowed_domains = allowed_domains or []
        self.blocked_domains = blocked_domains or []

    def __call__(self, value):
        domain = value.split("@")[-1].lower()

        if self.blocked_domains and domain in self.blocked_domains:
            raise ValidationError(f"Email domain '{domain}' is not allowed.")

        if self.allowed_domains and domain not in self.allowed_domains:
            raise ValidationError(
                f"Email domain '{domain}' is not in the allowed list."
            )

        return value


class PhoneNumberValidator:
    """
    Validates phone numbers with international format support.
    """

    def __init__(self, allow_international=True):
        self.allow_international = allow_international
        if allow_international:
            self.pattern = r"^\+?[1-9]\d{1,14}$"  # E.164 format
        else:
            self.pattern = r"^\d{10}$"  # US format (10 digits)

    def __call__(self, value):
        # Remove common separators
        cleaned = re.sub(r"[\s\-\(\)]", "", value)

        if not re.match(self.pattern, cleaned):
            if self.allow_international:
                raise ValidationError("Enter a valid phone number (e.g., +1234567890).")
            else:
                raise ValidationError("Enter a valid 10-digit phone number.")

        return cleaned


class UUIDValidator:
    """
    Validates UUID format.
    """

    def __call__(self, value):
        try:
            uuid.UUID(str(value))
        except ValueError:
            raise ValidationError("Enter a valid UUID.")
        return value


class UsernameValidator:
    """
    Validates username format and availability.
    """

    def __init__(self, min_length=3, max_length=30, allow_unicode=False):
        self.min_length = min_length
        self.max_length = max_length
        self.allow_unicode = allow_unicode

        if allow_unicode:
            self.pattern = r"^[\w\-]+$"
        else:
            self.pattern = r"^[a-zA-Z0-9_\-]+$"

    def __call__(self, value):
        if len(value) < self.min_length:
            raise ValidationError(
                f"Username must be at least {self.min_length} characters long."
            )

        if len(value) > self.max_length:
            raise ValidationError(
                f"Username must be no more than {self.max_length} characters long."
            )

        if not re.match(self.pattern, value):
            if self.allow_unicode:
                raise ValidationError(
                    "Username can only contain letters, numbers, underscores, and hyphens."
                )
            else:
                raise ValidationError(
                    "Username can only contain ASCII letters, numbers, underscores, and hyphens."
                )

        # Check for reserved usernames
        reserved_usernames = [
            "admin",
            "administrator",
            "root",
            "system",
            "api",
            "www",
            "mail",
            "ftp",
            "support",
            "help",
            "info",
            "contact",
            "webmaster",
            "postmaster",
        ]

        if value.lower() in reserved_usernames:
            raise ValidationError("This username is reserved and cannot be used.")

        return value


class FileExtensionValidator:
    """
    Validates file extensions.
    """

    def __init__(self, allowed_extensions):
        self.allowed_extensions = [ext.lower() for ext in allowed_extensions]

    def __call__(self, value):
        if hasattr(value, "name"):
            filename = value.name
        else:
            filename = str(value)

        extension = filename.split(".")[-1].lower() if "." in filename else ""

        if extension not in self.allowed_extensions:
            raise ValidationError(
                f"File extension '{extension}' is not allowed. "
                f"Allowed extensions: {', '.join(self.allowed_extensions)}"
            )

        return value


class FileSizeValidator:
    """
    Validates file size.
    """

    def __init__(self, max_size_mb):
        self.max_size_bytes = max_size_mb * 1024 * 1024

    def __call__(self, value):
        if hasattr(value, "size"):
            size = value.size
        else:
            size = len(value)

        if size > self.max_size_bytes:
            max_size_mb = self.max_size_bytes / (1024 * 1024)
            raise ValidationError(f"File size must be less than {max_size_mb:.1f} MB.")

        return value


class ImageDimensionValidator:
    """
    Validates image dimensions.
    """

    def __init__(
        self, max_width=None, max_height=None, min_width=None, min_height=None
    ):
        self.max_width = max_width
        self.max_height = max_height
        self.min_width = min_width
        self.min_height = min_height

    def __call__(self, value):
        try:
            from PIL import Image

            if hasattr(value, "read"):
                image = Image.open(value)
                value.seek(0)  # Reset file pointer
            else:
                image = Image.open(value)

            width, height = image.size

            if self.max_width and width > self.max_width:
                raise ValidationError(
                    f"Image width must be less than {self.max_width} pixels."
                )

            if self.max_height and height > self.max_height:
                raise ValidationError(
                    f"Image height must be less than {self.max_height} pixels."
                )

            if self.min_width and width < self.min_width:
                raise ValidationError(
                    f"Image width must be at least {self.min_width} pixels."
                )

            if self.min_height and height < self.min_height:
                raise ValidationError(
                    f"Image height must be at least {self.min_height} pixels."
                )

        except Exception as e:
            raise ValidationError("Invalid image file.")

        return value


class URLValidator:
    """
    Enhanced URL validator with additional checks.
    """

    def __init__(self, schemes=None, require_tld=True):
        self.schemes = schemes or ["http", "https"]
        self.require_tld = require_tld

    def __call__(self, value):
        from django.core.validators import URLValidator as DjangoURLValidator

        validator = DjangoURLValidator(schemes=self.schemes)

        try:
            validator(value)
        except ValidationError:
            raise ValidationError("Enter a valid URL.")

        if self.require_tld:
            from urllib.parse import urlparse

            parsed = urlparse(value)
            if "." not in parsed.netloc:
                raise ValidationError("URL must include a top-level domain.")

        return value


class CreditCardValidator:
    """
    Validates credit card numbers using Luhn algorithm.
    """

    def __call__(self, value):
        # Remove spaces and hyphens
        cleaned = re.sub(r"[\s\-]", "", value)

        if not cleaned.isdigit():
            raise ValidationError("Credit card number must contain only digits.")

        if len(cleaned) < 13 or len(cleaned) > 19:
            raise ValidationError(
                "Credit card number must be between 13 and 19 digits."
            )

        # Luhn algorithm check
        def luhn_check(card_num):
            def digits_of(n):
                return [int(d) for d in str(n)]

            digits = digits_of(card_num)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(d * 2))
            return checksum % 10 == 0

        if not luhn_check(cleaned):
            raise ValidationError("Invalid credit card number.")

        return cleaned


class DateRangeValidator:
    """
    Validates that a date falls within a specified range.
    """

    def __init__(self, start_date=None, end_date=None):
        self.start_date = start_date
        self.end_date = end_date

    def __call__(self, value):
        from datetime import date

        if isinstance(value, str):
            from django.utils.dateparse import parse_date

            value = parse_date(value)

        if self.start_date and value < self.start_date:
            raise ValidationError(f"Date must be on or after {self.start_date}.")

        if self.end_date and value > self.end_date:
            raise ValidationError(f"Date must be on or before {self.end_date}.")

        return value


class NumericRangeValidator:
    """
    Validates that a number falls within a specified range.
    """

    def __init__(self, min_value=None, max_value=None):
        self.min_value = min_value
        self.max_value = max_value

    def __call__(self, value):
        try:
            numeric_value = float(value)
        except (ValueError, TypeError):
            raise ValidationError("Value must be a number.")

        if self.min_value is not None and numeric_value < self.min_value:
            raise ValidationError(f"Value must be at least {self.min_value}.")

        if self.max_value is not None and numeric_value > self.max_value:
            raise ValidationError(f"Value must be no more than {self.max_value}.")

        return value


class JSONValidator:
    """
    Validates JSON format.
    """

    def __call__(self, value):
        import json

        if isinstance(value, (dict, list)):
            return value

        try:
            json.loads(value)
        except (json.JSONDecodeError, TypeError):
            raise ValidationError("Enter valid JSON.")

        return value


class RegexPatternValidator:
    """
    Validates text against a custom regex pattern.
    """

    def __init__(self, pattern, message=None, flags=0):
        self.pattern = pattern
        self.message = message or f"Value does not match required pattern: {pattern}"
        self.flags = flags

    def __call__(self, value):
        if not re.match(self.pattern, value, self.flags):
            raise ValidationError(self.message)

        return value


class NoSpecialCharactersValidator:
    """
    Validates that text contains no special characters.
    """

    def __init__(self, allow_spaces=True):
        self.allow_spaces = allow_spaces
        if allow_spaces:
            self.pattern = r"^[a-zA-Z0-9\s]+$"
        else:
            self.pattern = r"^[a-zA-Z0-9]+$"

    def __call__(self, value):
        if not re.match(self.pattern, value):
            if self.allow_spaces:
                raise ValidationError(
                    "Value can only contain letters, numbers, and spaces."
                )
            else:
                raise ValidationError("Value can only contain letters and numbers.")

        return value


# Common validator instances for reuse
validate_strong_password = PasswordStrengthValidator()
validate_phone_number = PhoneNumberValidator()
validate_uuid = UUIDValidator()
validate_username = UsernameValidator()
validate_json = JSONValidator()

# Regex validators for common patterns
validate_alphanumeric = RegexPatternValidator(
    r"^[a-zA-Z0-9]+$", "Value can only contain letters and numbers."
)

validate_slug = RegexPatternValidator(
    r"^[a-zA-Z0-9\-_]+$",
    "Value can only contain letters, numbers, hyphens, and underscores.",
)

validate_hex_color = RegexPatternValidator(
    r"^#[0-9A-Fa-f]{6}$", "Enter a valid hex color code (e.g., #FF5733)."
)

validate_postal_code = RegexPatternValidator(
    r"^\d{5}(-\d{4})?$", "Enter a valid postal code (e.g., 12345 or 12345-6789)."
)
