from django.contrib import admin
from .models import Level, Badge, UserPointProfile, PointActivity, UserBadge

admin.site.register(Level)
admin.site.register(Badge)
admin.site.register(UserPointProfile)
admin.site.register(PointActivity)
admin.site.register(UserBadge)
