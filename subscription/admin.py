from django.contrib import admin
from .models import CustomUser, Subscription ,ActivityLog , UserProfile # Import the necessary models

admin.site.register( UserProfile)
admin.site.register(CustomUser)
admin.site.register(Subscription)

admin.site.register(ActivityLog)