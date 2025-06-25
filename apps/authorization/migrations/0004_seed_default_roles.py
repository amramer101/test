from django.db import migrations

def create_roles(apps, schema_editor):
    Role = apps.get_model('authorization', 'Role')
    Permission = apps.get_model('authorization', 'Permission')
    # Define roles and their permissions
    roles = {
        "Student": [
            "view_point_profile", "view_point_activity", "view_balance", "view_spending_history", "view_leaderboard", "view_streaks", "view_achievements", "view_social_stats", "view_cosmetic_unlocks", "start_quest", "abandon_quest", "participate_events", "claim_quest_reward", "view_quests", "view_active_quests", "view_completed_quests", "view_challenges", "complete_challenges", "view_my_challenges", "view_challenge_leaderboard", "view_upcoming_events", "view_event_leaderboard", "view_my_event_participation", "showcase_badges", "view_achievement_progress", "view_achievement_milestones", "view_streak_leaderboard", "view_social_leaderboard", "view_quest_leaderboard", "view_my_rank", "view_rank_history", "post_comments", "like_content", "share_content", "create_discussions", "view_liked_content", "view_share_stats", "view_popular_shares", "view_popular_discussions", "view_trending_discussions", "generate_referral_code", "track_referral_click", "view_referral_stats", "view_followers", "view_following", "view_mutual_friends", "view_suggestions", "view_activity_feed", "mark_feed_read", "purchase_cosmetics", "equip_cosmetics", "view_inventory", "view_shop_categories", "view_shop_items", "view_purchases", "view_purchase_history", "update_profile", "update_preferences", "upload_profile_picture", "view_profile", "search_users", "view_course", "enroll_course", "view_sections", "view_lessons", "complete_lessons", "view_enrollments", "unenroll_course", "view_reviews", "create_review"
        ],
        "Instructor": [
            "manage_quests", "award_manual_points", "spend_points", "adjust_balance", "recalculate_balance", "moderate_comments", "moderate_discussions", "gift_items", "manage_inventory", "manage_shop", "manage_courses", "manage_sections", "manage_lessons", "manage_reviews"
        ],
        "Moderator": [
            "moderate_comments", "moderate_discussions", "process_refunds"
        ],
        "Admin": [
            perm.codename for perm in Permission.objects.all()
        ],
    }
    for role_name, perm_codenames in roles.items():
        role, _ = Role.objects.get_or_create(name=role_name)
        perms = Permission.objects.filter(codename__in=perm_codenames)
        role.permissions.set(perms)
        role.save()

def reverse_roles(apps, schema_editor):
    Role = apps.get_model('authorization', 'Role')
    Role.objects.filter(name__in=["Student", "Instructor", "Moderator", "Admin"]).delete()

class Migration(migrations.Migration):
    dependencies = [
        ("authorization", "0003_seed_permissions"),
    ]
    operations = [
        migrations.RunPython(create_roles, reverse_roles),
    ]
