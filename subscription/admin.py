from django.contrib import admin
from .models import User, Subscription, Canvas, SavedWork  # Import the necessary models

 
# admin.site.register(User)
admin.site.register(Subscription)
admin.site.register(Canvas)
admin.site.register(SavedWork)
