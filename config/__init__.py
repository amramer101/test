"""
RM Platform Django Configuration Package

This package contains all Django configuration modules organized by environment.
"""

from .celery import app as celery_app

__all__ = ("celery_app",)
