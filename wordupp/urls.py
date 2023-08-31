from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView  # Import here

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('subscription/', include('subscription.urls')),  # Include subscription app URLs
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),  # Specify custom template
    path('logout/', LogoutView.as_view(), name='logout'),
]
