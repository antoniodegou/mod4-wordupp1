from django.urls import path
from .views import register_view, user_dashboard
from . import views
from django.urls import path, include
from django.contrib.auth.views import PasswordChangeView


urlpatterns = [
    path('change-password/', PasswordChangeView.as_view(), name='password_change'),
    # path('register/', register_view, name='register'),
    # path('dashboard/', views.user_dashboard, name='dashboard'),  # Changed name to be unique
    path('payment_success/', views.payment_success, name='payment_success'),
    path('webhooks/stripe/', views.stripe_webhook, name='stripe-webhook'),
]
