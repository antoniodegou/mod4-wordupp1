from django.db import models
from django.conf import settings
from datetime import datetime, timedelta
from django.contrib.auth.models import AbstractUser, UserManager as DefaultUserManager
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import models

 



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

# Canvas Model
class Canvas(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='canvases')

    name = models.CharField(max_length=255)
    canvas_data = models.TextField()
    thumbnail = models.ImageField(upload_to='canvas_thumbnails/', blank=True, null=True)
    tags = models.ManyToManyField('Tag', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# Tag Model
class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

# Saved Work Model
class SavedWork(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_works')
    canvas_data = models.JSONField()
    version = models.IntegerField(default=1)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_modified_date = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.user.username}'s saved work"

def get_current_datetime():
    return timezone.now()

# Subscription Model
class Subscription(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(default=timezone.now)  # Consider using a custom function to set a future date
    is_premium = models.BooleanField(default=False)
    stripe_subscription_id = models.CharField(max_length=255, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)



 
    STRIPE_PLAN_CHOICES = [
        ('price_1NmG4RCOAyay7VTLqfqUxOud', 'Free'),
        ('price_1NmG4RCOAyay7VTLPcRACV7i', 'Premium'),
    ]
    stripe_plan_id = models.CharField(
        max_length=50,
        choices=STRIPE_PLAN_CHOICES,
        default='price_1NmG4RCOAyay7VTLqfqUxOud',
    )

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('past_due', 'Past Due'),
        ('canceled', 'Canceled'),
        ('incomplete', 'Incomplete'),
        ('incomplete_expired', 'Incomplete Expired'),
        ('trialing', 'Trialing'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='incomplete',
    )


    
    def is_active(self):
       return self.status == 'active' and self.end_date > datetime.now()

    def __str__(self):
        return f"{self.user.username}'s Subscription"



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
 