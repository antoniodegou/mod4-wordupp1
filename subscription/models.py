from django.contrib.auth.models import AbstractUser
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
# from django.contrib import messages
from django.db import models
from django.conf import settings  # Import settings to get the custom user model
from django.contrib.auth.models import User
from datetime import datetime, timedelta
# from django.shortcuts import render, redirect
# from .forms import SubscriptionForm  # Importing SubscriptionForm from forms.py
# from .models import Subscription 
# from .forms import SubscriptionForm

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

 
# Saved Work Model
class SavedWork(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='saved_works')
    canvas_data = models.JSONField()  # You can choose the appropriate field type based on your data
    creation_date = models.DateTimeField(auto_now_add=True)
    last_modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s saved work"
    
 
class Subscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    start_date = models.DateTimeField(default=datetime.now)
    end_date = models.DateTimeField(default=datetime.now)
    is_premium = models.BooleanField(default=False)
    stripe_subscription_id = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Subscription"