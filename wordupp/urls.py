from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView  # Import here
from subscription.views import profile_view 
from subscription.views import user_dashboard  # Import the view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('subscription/', include('subscription.urls')),  # Include subscription app URLs
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),  # Specify custom template
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),  # Redirect to login page after logout
    path('profile/', profile_view, name='profile'),  # Add this line for the profile page
    path('dashboard/', user_dashboard, name='dashboard'),  # Add this line for the dashboard

]
