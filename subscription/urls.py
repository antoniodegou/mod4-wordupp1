from django.urls import path
from . import views
from .views import register_view, dashboard_view

urlpatterns = [
    path('create/', views.create_subscription, name='create_subscription'),
    path('success/', views.subscription_success, name='subscription_success'),
    path('register/', register_view, name='register'),
    path('dashboard/', dashboard_view, name='dashboard'),
   
]
