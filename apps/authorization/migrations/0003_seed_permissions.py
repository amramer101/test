from django.db import migrations

def create_permissions(apps, schema_editor):
    Permission = apps.get_model('authorization', 'Permission')
    permissions = [
        # Gamification
        ("start_quest", "Start new quests"),
        ("abandon_quest", "Abandon active quests"),
        ("manage_quests", "Admin quest management"),
        ("participate_events", "Participate in time-limited events"),
        ("view_point_profile", "View point profile"),
        ("view_point_activity", "View point activity"),
        ("view_balance", "View balance"),
        ("view_spending_history", "View spending history"),
        ("view_leaderboard", "View leaderboard"),
        ("view_streaks", "View streaks"),
        ("view_achievements", "View achievements"),
        ("view_social_stats", "View social stats"),
        ("view_cosmetic_unlocks", "View cosmetic unlocks"),
        ("award_manual_points", "Award manual points"),
        ("spend_points", "Spend points"),
        ("adjust_balance", "Adjust balance"),
        ("recalculate_balance", "Recalculate balance"),
        ("claim_quest_reward", "Claim quest reward"),
        ("view_quests", "View quests"),
        ("view_active_quests", "View active quests"),
        ("view_completed_quests", "View completed quests"),
        ("view_challenges", "View challenges"),
        ("complete_challenges", "Complete challenges"),
        ("view_my_challenges", "View my challenges"),
        ("view_challenge_leaderboard", "View challenge leaderboard"),
        ("view_upcoming_events", "View upcoming events"),
        ("view_event_leaderboard", "View event leaderboard"),
        ("view_my_event_participation", "View my event participation"),
        ("showcase_badges", "Showcase badges"),
        ("view_achievement_progress", "View achievement progress"),
        ("view_achievement_milestones", "View achievement milestones"),
        ("view_streak_leaderboard", "View streak leaderboard"),
        ("view_social_leaderboard", "View social leaderboard"),
        ("view_quest_leaderboard", "View quest leaderboard"),
        ("view_my_rank", "View my rank"),
        ("view_rank_history", "View rank history"),
        # Social
        ("post_comments", "Post comments"),
        ("moderate_comments", "Moderate comments"),
        ("like_content", "Like content"),
        ("share_content", "Share content"),
        ("create_discussions", "Create discussions"),
        ("moderate_discussions", "Moderate discussions"),
        ("view_liked_content", "View liked content"),
        ("view_share_stats", "View share stats"),
        ("view_popular_shares", "View popular shares"),
        ("view_popular_discussions", "View popular discussions"),
        ("view_trending_discussions", "View trending discussions"),
        ("generate_referral_code", "Generate referral code"),
        ("track_referral_click", "Track referral click"),
        ("view_referral_stats", "View referral stats"),
        ("view_followers", "View followers"),
        ("view_following", "View following"),
        ("view_mutual_friends", "View mutual friends"),
        ("view_suggestions", "View suggestions"),
        ("view_activity_feed", "View activity feed"),
        ("mark_feed_read", "Mark feed as read"),
        # Shop
        ("purchase_cosmetics", "Purchase cosmetics"),
        ("gift_items", "Gift items"),
        ("manage_inventory", "Manage inventory"),
        ("equip_cosmetics", "Equip cosmetics"),
        ("view_inventory", "View inventory"),
        ("view_shop_categories", "View shop categories"),
        ("manage_shop", "Manage shop"),
        ("view_shop_items", "View shop items"),
        ("view_purchases", "View purchases"),
        ("process_refunds", "Process refunds"),
        ("view_purchase_history", "View purchase history"),
        # Users
        ("update_profile", "Update profile"),
        ("update_preferences", "Update preferences"),
        ("upload_profile_picture", "Upload profile picture"),
        ("view_profile", "View profile"),
        ("search_users", "Search users"),
        # Courses
        ("view_course", "View course"),
        ("create_course", "Create course"),
        ("manage_courses", "Manage courses"),
        ("enroll_course", "Enroll in course"),
        ("view_sections", "View sections"),
        ("manage_sections", "Manage sections"),
        ("view_lessons", "View lessons"),
        ("manage_lessons", "Manage lessons"),
        ("complete_lessons", "Complete lessons"),
        ("view_enrollments", "View enrollments"),
        ("unenroll_course", "Unenroll from course"),
        ("view_reviews", "View reviews"),
        ("create_review", "Create review"),
        ("manage_reviews", "Manage reviews"),
    ]
    for codename, name in permissions:
        Permission.objects.get_or_create(codename=codename, defaults={"name": name})

def reverse_permissions(apps, schema_editor):
    Permission = apps.get_model('authorization', 'Permission')
    Permission.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ("authorization", "0002_role_permissions"),
    ]
    operations = [
        migrations.RunPython(create_permissions, reverse_permissions),
    ]
