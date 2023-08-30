from django.urls import path
from . import views
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('create/', views.create_subscription, name='create_subscription'),
    path('success/', views.subscription_success, name='subscription_success'),
    path('accounts/login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    # path('signup/', views.signup_view, name='signup'),  # Add this line
    # path('signup/', views.signup_view, name='signup'),  # Remove or comment out this line

]