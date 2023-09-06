from django.urls import path
from .views import register_view, user_dashboard
from . import views
 

urlpatterns = [
    # path('register/', register_view, name='register'),
    # path('dashboard/', views.user_dashboard, name='dashboard'),  # Changed name to be unique
    path('payment_success/', views.payment_success, name='payment_success'),
    path('webhooks/stripe/', views.stripe_webhook, name='stripe-webhook'),
]
