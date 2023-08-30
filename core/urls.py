from django.urls import path, include
from . import views
app_name = 'core'



urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('pricing/', views.pricing, name='pricing'),
    path('tutorials/', views.tutorials, name='tutorials'),
    path('contact/', views.contact, name='contact'),
]