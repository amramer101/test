import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")

app = Celery("RM_Platform")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.update(
    broker_url=os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    result_backend=os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/1"),
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "reset-daily-streaks": {
            "task": "apps.gamification.tasks.reset_daily_streaks",
            "schedule": crontab(minute=0, hour=0),
        },
        "update-leaderboards": {
            "task": "apps.gamification.tasks.update_leaderboards",
            "schedule": crontab(minute=30, hour=0),
        },
        "expire-events": {
            "task": "apps.gamification.tasks.expire_events",
            "schedule": crontab(minute="*/30"),
        },
        "reset-weekly-challenges": {
            "task": "apps.gamification.tasks.reset_weekly_challenges",
            "schedule": crontab(minute=0, hour=0, day_of_week=1),
        },
        "check-quest-deadlines": {
            "task": "apps.gamification.tasks.check_quest_deadlines",
            "schedule": crontab(minute=0, hour="*"),
        },
        "award-daily-login-streaks": {
            "task": "apps.gamification.tasks.award_daily_login_streaks",
            "schedule": crontab(minute=0, hour="*"),
        },
    },
)


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
