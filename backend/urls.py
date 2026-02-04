from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('manage-reviews/', views.manage_reviews, name='manage_reviews'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('home/', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('manage-messages/', views.manage_messages, name='manage_messages'),
    
]