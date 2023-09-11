from django.db import models
from django.conf import settings
from datetime import datetime, timedelta
from django.contrib.auth.models import AbstractUser, UserManager as DefaultUserManager
from django.utils import timezone
# from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, blank=False, null=False)

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.user.email

STRIPE_PLAN_CHOICES = [
    ('price_1NmG4RCOAyay7VTLqfqUxOud', 'Free'),
    ('price_1NmG4RCOAyay7VTLPcRACV7i', 'Premium'),
    # ('free_plan_id', 'Free'),
    # ('premium_plan_id', 'Premium')
]

STATUS_CHOICES = [
    ('active', 'Active'),
    ('past_due', 'Past Due'),
    ('canceled', 'Canceled'),
    ('incomplete', 'Incomplete'),
    ('incomplete_expired', 'Incomplete Expired'),
    ('trialing', 'Trialing'),
]



# Tag Model
class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name



# Subscription Model
class Subscription(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='subscription')
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    stripe_plan_id = models.CharField(max_length=50, choices=STRIPE_PLAN_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    stripe_subscription_id = models.CharField(max_length=50, blank=True, null=True)  # Store the Stripe subscription ID if needed

    def __str__(self):
        return f"{self.user_profile.user.email}'s Subscription"

    def is_active(self):
        return self.status == 'active' and self.end_date > timezone.now()





class ActivityLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='activity_logs')
    activity = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
