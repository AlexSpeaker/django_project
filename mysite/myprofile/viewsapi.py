from django.contrib.auth import login
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Profile
from .serializers import ProfileSerializer, UserPasswordSerializer


class ProfileAPIView(APIView):
    model = Profile
    serializer = ProfileSerializer

    def get(self, request: Request, *args, **kwargs) -> Response:
        user = self.request.user
        if not user.is_authenticated:
            message_error = {'error': 'Authentication Error'}
            return Response(data=message_error, status=status.HTTP_404_NOT_FOUND)
        profile, created = self.model.objects.get_or_create(user=user)
        profile_serializer = self.serializer(profile)
        return Response(profile_serializer.data)

    def post(self, request: Request, *args, **kwargs) -> Response:
        user = self.request.user
        if not user.is_authenticated:
            message_error = {'error': 'Authentication Error'}
            return Response(data=message_error, status=status.HTTP_404_NOT_FOUND)
        data = request.data
        data.pop('avatar')
        profile, created = self.model.objects.get_or_create(user=user)
        profile_serializer = self.serializer(data=data, instance=profile)
        if profile_serializer.is_valid():
            profile_serializer.update(profile, data)
            return Response(profile_serializer.data)
        message_error = {'error': 'Incorrect data'}
        return Response(data=message_error, status=status.HTTP_400_BAD_REQUEST)


class AvatarAPIView(APIView):
    model = Profile
    serializer = ProfileSerializer

    def post(self, request: Request, *args, **kwargs) -> Response:
        user = self.request.user
        if not user.is_authenticated:
            message_error = {'error': 'Authentication Error'}
            return Response(data=message_error, status=status.HTTP_404_NOT_FOUND)
        profile, created = self.model.objects.get_or_create(user=user)
        data = request.data
        avatar_serializer = self.serializer(data=data, instance=profile)
        if avatar_serializer.is_valid():
            avatar_serializer.update(profile, data)
            return Response(status=status.HTTP_200_OK)
        message_error = {'error': 'Incorrect data'}
        return Response(data=message_error, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordAPIView(APIView):
    model = User
    serializer = UserPasswordSerializer

    def post(self, request: Request, *args, **kwargs) -> Response:
        current_user = self.request.user
        if not current_user.is_authenticated:
            message_error = {'error': 'Authentication Error'}
            return Response(data=message_error, status=status.HTTP_404_NOT_FOUND)
        user = self.model.objects.get(pk=current_user.pk)
        if not user.check_password(request.data['currentPassword']):
            message_error = {'error': 'Incorrect current password'}
            return Response(data=message_error, status=status.HTTP_400_BAD_REQUEST)
        data = dict(password=request.data['newPassword'])
        user_password_serializer = self.serializer(data=data, instance=user)
        if user_password_serializer.is_valid():
            user.set_password(request.data['newPassword'])
            user.save()
            login(request=request, user=user)
            return Response(status=status.HTTP_200_OK)
        message_error = {'error': 'Incorrect new password'}
        return Response(data=message_error, status=status.HTTP_400_BAD_REQUEST)
