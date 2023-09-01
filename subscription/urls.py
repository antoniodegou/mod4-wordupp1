from django.urls import path
from .views import register_view, user_dashboard

 

urlpatterns = [
    path('register/', register_view, name='register'),
    path('dashboard/', user_dashboard, name='dashboard'),  # Changed name to be unique
]
