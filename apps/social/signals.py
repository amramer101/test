from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import (
    Comment,
    Like,
    Share,
    Discussion,
    DiscussionReply,
    Referral,
    UserFollowing,
    ActivityFeed,
)
from apps.gamification.utils import award_social_points, update_referral_progress


# --- Comment Signals ---
@receiver(post_save, sender=Comment)
def comment_created(sender, instance, created, **kwargs):
    if created:
        award_social_points(instance.user, "comment_posted", instance)


# --- Like Signals ---
@receiver(post_save, sender=Like)
def like_created(sender, instance, created, **kwargs):
    if created:
        award_social_points(instance.user, "like_given", instance)
        # Award points to content creator if possible
        target = instance.content_object
        if hasattr(target, "user"):
            award_social_points(target.user, "like_received", target)


# --- Share Signals ---
@receiver(post_save, sender=Share)
def share_created(sender, instance, created, **kwargs):
    if created:
        award_social_points(instance.user, "content_shared", instance)
        target = instance.content_object
        if hasattr(target, "user"):
            award_social_points(target.user, "content_shared_by_others", target)


# --- Discussion Signals ---
@receiver(post_save, sender=Discussion)
def discussion_created(sender, instance, created, **kwargs):
    if created:
        award_social_points(instance.created_by, "discussion_started", instance)


@receiver(post_save, sender=DiscussionReply)
def discussion_reply_created(sender, instance, created, **kwargs):
    if created:
        award_social_points(instance.user, "discussion_reply", instance)


# --- Referral Signals ---
@receiver(post_save, sender=Referral)
def referral_completed(sender, instance, **kwargs):
    if instance.status == "completed" and instance.points_awarded == 0:
        update_referral_progress(instance.referrer, instance.referred_user)


# --- UserFollowing Signals ---
@receiver(post_save, sender=UserFollowing)
def following_created(sender, instance, created, **kwargs):
    if created:
        award_social_points(instance.follower, "follow_user", instance)
        award_social_points(instance.following, "gained_follower", instance)


# --- ActivityFeed Signals ---
@receiver(post_save, sender=ActivityFeed)
def activity_feed_created(sender, instance, created, **kwargs):
    if created:
        award_social_points(instance.user, "activity_feed", instance)
