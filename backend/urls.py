from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('manage-reviews/', views.manage_reviews, name='manage_reviews'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('home/', views.home, name='home'),
    path('manage-messages/', views.manage_messages, name='manage_messages'),
    path('logout/', views.logout_view, name='logout'),
    path('login/', views.login_view, name='login'),
    path('staff/add/', views.manage_staff_member, name='add_staff'),
    path('staff/edit/<int:user_id>/', views.manage_staff_member, name='edit_staff'),
    path('staff/manage/', views.manage_staff_member, name='manage_staff'),
    
]