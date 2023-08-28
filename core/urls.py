from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('pricing/', views.pricing, name='pricing'),
    path('tutorials/', views.tutorials, name='tutorials'),
    path('contact/', views.contact, name='contact'),
]