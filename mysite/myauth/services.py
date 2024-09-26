import json
from typing import Optional

from django.contrib.auth.models import User
from django.db.models import Q
from django.http import QueryDict
from rest_framework.request import Request

from shopapp.models import Basket, Order


def get_user_data(data_request: QueryDict) -> Optional[dict]:
    """
    Извлекает из ключа request.data необходимые данные пользователя
    :param data_request: request.data
    :return: dict(first_name=first_name, username=username, password=password)
    """
    user_data_list = [data for data in data_request if 'username' in data and 'password' in data]
    if user_data_list:
        user_data_dict = json.loads(user_data_list[0])
        data = dict(
            first_name=user_data_dict.get('name', ''),
            username=user_data_dict['username'],
            password=user_data_dict['password']
        )
        return data
    return None

def get_and_update_baskets_orders(user: User, request: Request) -> None:
    """
    Функция после аутентификация пользователя проверяет анонимный токен и добавляет ему его анонимные basket и order
    :param user:
    :param request:
    :return:
    """
    token = request.session.get('user', None)
    if token:
        baskets_old = Basket.objects.filter(Q(archived=False) & Q(user_auth_user=user))
        baskets_old.update(archived=True)
        baskets = Basket.objects.filter(Q(archived=False) & Q(user=token))
        if baskets:
            baskets.update(user=None, user_auth_user=user)
        orders = Order.objects.filter(user=token)
        if orders:
            orders.update(user=None, user_auth_user=user)
