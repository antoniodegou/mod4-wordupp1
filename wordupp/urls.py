from django.contrib import admin
from django.urls import path, include
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from subscription.views import register_view, user_dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('subscription/', include('subscription.urls')),
    path('dashboard/', user_dashboard, name='dashboard'),
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('register/', register_view, name='register'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

]
