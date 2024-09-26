
from django.urls import path

from .viewsapi import RegisterUserAPIView, UserLogout, UserLogin

app_name = "myauth"


urlpatterns = [
    path('api/sign-up', RegisterUserAPIView.as_view(), name='post_sign_up'),
    path('api/sign-out', UserLogout.as_view(), name='post_sign_out'),
    path('api/sign-in', UserLogin.as_view(), name='post_sign_in'),
]
