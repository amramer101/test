import random
import string
import re
from datetime import datetime, timedelta
from django.utils.text import slugify
from django.utils import timezone


def generate_random_string(length=12):
    """Generate a random alphanumeric string of given length."""
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def humanize_timedelta(td):
    """Convert a timedelta to a human-readable string."""
    seconds = int(td.total_seconds())
    periods = [
        ("year", 60 * 60 * 24 * 365),
        ("month", 60 * 60 * 24 * 30),
        ("day", 60 * 60 * 24),
        ("hour", 60 * 60),
        ("minute", 60),
        ("second", 1),
    ]
    strings = []
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            strings.append(
                f"{period_value} {period_name}{'s' if period_value > 1 else ''}"
            )
    return ", ".join(strings) or "0 seconds"


def unique_slugify(instance, value, slug_field_name="slug"):
    """Generates a unique slug for a model instance."""
    slug = slugify(value)
    ModelClass = instance.__class__
    unique_slug = slug
    num = 1
    while ModelClass.objects.filter(**{slug_field_name: unique_slug}).exists():
        unique_slug = f"{slug}-{num}"
        num += 1
    return unique_slug


def is_valid_email(email):
    """Simple regex-based email validation."""
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None


def is_valid_phone(phone):
    """Simple regex-based phone validation (international format)."""
    return re.match(r"^\+?1?\d{9,15}$", phone) is not None


def format_file_size(size_bytes):
    """Format file size in bytes to a human-readable string."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"


# Add more shared utility functions here as needed
