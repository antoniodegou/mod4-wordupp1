from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_subscription, name='create_subscription'),
    path('success/', views.subscription_success, name='subscription_success'),
]
