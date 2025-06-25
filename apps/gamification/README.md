# Gamification App

A Django app for user engagement through points, levels, badges, and activity logging, inspired by Microsoft Learn.

## Features
- Award points for user actions (registration, login, etc.)
- User levels based on total points, with progress bar
- Badges for achievements, with customizable criteria
- Activity log of point-earning events
- Admin management of levels and badges
- REST API endpoints for user profile, levels, badges, and awarding
- Automatic point and badge awarding via signals

## Models
- **Level**: Defines user levels and required points
- **Badge**: Defines badges, descriptions, icons, and JSON criteria
- **UserPointProfile**: Tracks user points, level, and progress
- **PointActivity**: Logs each point-earning event
- **UserBadge**: Tracks which badges a user has earned

## Signals
- Listens to `user_created` (registration) and `user_logged_in` (login) signals
- Automatically awards points and checks for badge eligibility

## Badge Criteria
- Store criteria as JSON in the `Badge` model, e.g.:
  ```json
  {"points": 1000, "actions": ["login", "complete_lesson"]}
  ```
- Criteria are checked after each point-earning event
- Extend `badge_criteria_met` in `utils.py` for custom logic

## API Endpoints
- `/api/v1/gamification/profile/` — User's points, level, progress, badges
- `/api/v1/gamification/levels/` — List all levels
- `/api/v1/gamification/badges/` — List all badges
- `/api/v1/gamification/award/award_points/` — Admin: award points
- `/api/v1/gamification/award/award_badge/` — Admin: award badge

## Extension Points
- Add more signal receivers in `signals.py` for new actions
- Expand badge criteria logic in `utils.py`
- Add new levels and badges via Django admin

## Setup
1. Add `apps.gamification` to `INSTALLED_APPS`
2. Run migrations: `python manage.py makemigrations gamification && python manage.py migrate`
3. Add levels and badges in Django admin
4. Use or extend the API endpoints as needed

---
For more details, see the code in `models.py`, `utils.py`, and `signals.py`. 