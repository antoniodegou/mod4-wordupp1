from django.urls import path
from . import views
from .views import register_view, dashboard_view
# from .views import user_dashboard  # Or however you've organized your imports
from subscription.views import user_dashboard
urlpatterns = [
    path('create/', views.create_subscription, name='create_subscription'),
    path('success/', views.subscription_success, name='subscription_success'),
    path('register/', register_view, name='register'),
    # path('dashboard/', user_dashboard, name='dashboard'),  # Add this line for the dashboard
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
]
