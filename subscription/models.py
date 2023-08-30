from django.contrib.auth.models import AbstractUser
from django.db import models

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
    SUBSCRIPTION_CHOICES = [
        ('free', 'Free'),
        ('premium', 'Premium'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    subscription_type = models.CharField(max_length=10, choices=SUBSCRIPTION_CHOICES, default='free')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.subscription_type}"