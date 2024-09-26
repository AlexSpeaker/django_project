from django.urls import path
from .viewsapi import ProfileAPIView, AvatarAPIView, ChangePasswordAPIView

app_name = "myprofile"

urlpatterns = [
    path('api/profile', ProfileAPIView.as_view(), name='profile-api'),
    path('api/profile/avatar', AvatarAPIView.as_view(), name='profile-avatar-api'),
    path('api/profile/password', ChangePasswordAPIView.as_view(), name='profile-password-api')
]
