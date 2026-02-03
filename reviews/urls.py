from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add-review/<slug:slug>/', views.submit_review, name='submit_review'),
    path('review/<int:review_id>/', views.review_detail, name='review_detail'),
    path('user/<int:user_id>/', views.user_profile, name='user_profile'),
    path('add-reply/', views.add_reply, name='add_reply')
]