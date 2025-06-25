# Shared constants for use across the platform

# Status choices
STATUS_ACTIVE = "active"
STATUS_INACTIVE = "inactive"
STATUS_PENDING = "pending"
STATUS_DELETED = "deleted"

STATUS_CHOICES = [
    (STATUS_ACTIVE, "Active"),
    (STATUS_INACTIVE, "Inactive"),
    (STATUS_PENDING, "Pending"),
    (STATUS_DELETED, "Deleted"),
]

# Action types
ACTION_CREATE = "create"
ACTION_UPDATE = "update"
ACTION_DELETE = "delete"
ACTION_VIEW = "view"
ACTION_LOGIN = "login"
ACTION_LOGOUT = "logout"

ACTION_CHOICES = [
    (ACTION_CREATE, "Create"),
    (ACTION_UPDATE, "Update"),
    (ACTION_DELETE, "Delete"),
    (ACTION_VIEW, "View"),
    (ACTION_LOGIN, "Login"),
    (ACTION_LOGOUT, "Logout"),
]
