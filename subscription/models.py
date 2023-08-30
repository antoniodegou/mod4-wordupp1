from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db import models
from django.conf import settings  # Import settings to get the custom user model
from django.utils import timezone


class CustomUser(AbstractUser):
    # You can add additional fields here if needed

    # Add these lines to solve the reverse accessor issue
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name="customuser_set",
        related_query_name="user",
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="customuser_set",
        related_query_name="user",
    )


class Canvas(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='canvases')
    name = models.CharField(max_length=255)
    canvas_data = models.TextField()  # You can use JSONField if you're on Django 3.1+
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Subscription(models.Model):
    SUBSCRIPTION_TYPE_CHOICES = [
        ('basic', 'Basic'),
        ('premium', 'Premium'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='subscription')
    subscription_type = models.CharField(max_length=20, choices=SUBSCRIPTION_TYPE_CHOICES, default='basic')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive')
    start_date = models.DateField()
    end_date = models.DateField()
    
# Saved Work Model
class SavedWork(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='saved_works')
    canvas_data = models.JSONField()  # You can choose the appropriate field type based on your data
    creation_date = models.DateTimeField(auto_now_add=True)
    last_modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s saved work"
    

class Subscription(models.Model):
    BASIC = 'basic'
    PREMIUM = 'premium'
    PLATINUM = 'platinum'

    PLAN_CHOICES = [
        (BASIC, 'Basic'),
        (PREMIUM, 'Premium'),
        (PLATINUM, 'Platinum'),
    ]

    ACTIVE = 'active'
    INACTIVE = 'inactive'
    CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (INACTIVE, 'Inactive'),
        (CANCELLED, 'Cancelled'),
    ]

    plan = models.CharField(max_length=10, choices=PLAN_CHOICES, default=BASIC)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(default=timezone.now)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Changed to settings.AUTH_USER_MODEL
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=INACTIVE)

    def __str__(self):
        return f"{self.user.username}'s {self.plan} subscription"