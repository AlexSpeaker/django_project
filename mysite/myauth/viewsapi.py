from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserSerializer
from myprofile.models import Profile
from .services import get_user_data, get_and_update_baskets_orders


class RegisterUserAPIView(APIView):
    model = User
    serializer = UserSerializer

    def post(self, request: Request, *args, **kwargs) -> Response:
        data = get_user_data(request.data)
        if data is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user_serializer = self.serializer(data=data)
        if not user_serializer.is_valid():
            message_error = {'error': 'Incorrect data'}
            return Response(data=message_error, status=status.HTTP_400_BAD_REQUEST)
        password = data.pop('password')
        user = user_serializer.create(data)
        user.set_password(password)
        user.save()
        Profile.objects.create(user=user)
        get_and_update_baskets_orders(user, request)
        login(request=request, user=user)
        return Response(status=status.HTTP_200_OK)


class UserLogout(APIView):
    @classmethod
    def post(cls, request: Request, *args, **kwargs) -> Response:
        logout(request)
        return Response(status=status.HTTP_200_OK)


class UserLogin(APIView):
    model = User

    def post(self, request: Request, *args, **kwargs) -> Response:
        data = get_user_data(request.data)
        if data:
            user = get_object_or_404(self.model, username=data['username'])
            if user.check_password(data['password']):
                get_and_update_baskets_orders(user, request)
                login(request=request, user=user)
                return Response(status=status.HTTP_200_OK)
        message_error = {'error': 'Incorrect data'}
        return Response(data=message_error, status=status.HTTP_400_BAD_REQUEST)
