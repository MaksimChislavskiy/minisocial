from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('post/create/', views.create_post, name='create_post'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/<int:pk>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:pk>/delete/', views.delete_post, name='delete_post'),
    path('post/<int:pk>/like/', views.like_post, name='like_post'),
    path('user/<str:username>/', views.profile, name='profile'),
    path('user/<str:username>/follow/', views.follow_user, name='follow_user'),
]