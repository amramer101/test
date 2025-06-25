from django.dispatch import Signal

user_created = Signal()
user_updated = Signal()
user_deleted = Signal()

# Usage example (in any app):
# from apps.shared.signals import user_created
# user_created.send(sender=User, user=user_instance, created_by=admin_user)
