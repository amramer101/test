from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from apps.shared.signals import user_created
from django.conf import settings
from .utils import award_points


@receiver(user_created)
def award_points_on_registration(sender, user, created_by, **kwargs):
    award_points(user, points=100, action="register", description="Registration bonus")


@receiver(user_logged_in)
def award_points_on_login(sender, user, request, **kwargs):
    award_points(user, points=10, action="login", description="Login bonus")
