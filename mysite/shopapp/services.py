import uuid
from calendar import monthrange
from collections import Counter
from datetime import datetime, date
from typing import Optional

from django.contrib.auth.models import User
from django.db.models import Q
from django.http import QueryDict
from rest_framework.request import Request

from mysite.settings import MEDIA_URL
from shopapp.models import Product


def get_popular_tags(data: list) -> list:
    """
    Принимает список из тегов [{name='name', id='id'}, ...],
    и возвращает список из уникальных тегов [{name='name', id='id'}, ...] отсортированных по популярности.
    :param data:
    :return:
    """
    popular_name_dict = Counter([(data['name'], data['id']) for data in data])
    popular_name_list = sorted(popular_name_dict, key=lambda k: popular_name_dict[k], reverse=True)
    response_data = [dict(name=item[0], id=item[1]) for item in popular_name_list]
    return response_data


def get_filter_param(data_request: QueryDict) -> list:
    """
    Получает данные request запроса и формирует список с параметрами для фильтрации queryset
    :param data_request:
    :return:
    """
    filter_param = []

    filter_name = data_request.get('filter[name]', None)
    if filter_name:
        filter_param.append(Q(title__contains=filter_name))

    filter_min_price = data_request.get('filter[minPrice]', None)
    filter_max_price = data_request.get('filter[maxPrice]', None)
    if filter_min_price and filter_max_price and (int(filter_max_price) >= int(filter_min_price)):
        filter_param.append(Q(price__range=[filter_min_price, filter_max_price]))

    category = data_request.get('category', None)
    if category and int(category) // 10e6:
        category = int(int(category) % 10e6)
        filter_param.append(Q(category__category=category))
    elif category:
        filter_param.append(Q(category=category))

    filter_free_delivery = data_request.get('filter[freeDelivery]', None)
    if filter_free_delivery == 'true':
        filter_param.append(Q(freeDelivery=True))

    filter_available = data_request.get('filter[available]', None)
    if filter_available == 'true':
        filter_param.append(Q(count__gt=0))

    tags_list = data_request.getlist('tags[]', None)
    if tags_list and len(tags_list):
        filter_param.append(Q(tags__in=tags_list))

    return filter_param


def get_user_param_create_token(request: Request) -> Optional[dict]:
    """
    Функция принимает на себя request запроса.
    Если пользователь не прошёл аутентификацию, функция проверит токен анонимного пользователя.
    Если пользователь не прошёл аутентификацию и токен отсутствует:
    Функция создаст новый токен анонимного пользователя
    и вернёт: user_param['user'] = token
    Если пользователь не прошёл аутентификацию и токен найден:
    Функция вернёт: user_param['user'] = token
    Если пользователь прошёл аутентификацию:
    Функция вернёт: user_param['user_auth_user'] = request.user
    :param request:
    :return:
    """
    user = request.user
    user_param = {}
    if not user.is_authenticated:
        token = request.session.get('user', None) or uuid.uuid4().hex
        request.session['user'] = token
        user_param['user'] = token
    else:
        user_param['user_auth_user'] = user
    return user_param


def get_user_param_no_create_token(request: Request) -> Optional[dict]:
    """
    Функция принимает на себя request запроса.
    Если пользователь не прошёл аутентификацию, функция проверит токен анонимного пользователя.
    Если пользователь не прошёл аутентификацию и токен отсутствует:
    Функция вернёт: None
    Если пользователь не прошёл аутентификацию и токен найден:
    Функция вернёт: user_param['user'] = token
    Если пользователь прошёл аутентификацию:
    Функция вернёт: user_param['user_auth_user'] = request.user
    :param request:
    :return:
    """
    user = request.user
    user_param = {}
    if user.is_authenticated:
        user_param['user_auth_user'] = user
    else:
        token = request.session.get('user', None)
        if token is None:
            return None
        user_param['user'] = token
    return user_param


def get_fullname_email_phone(user: User) -> tuple:
    """
    Функция принимает текущего пользователя и возвращает его:
     полное имя (ищет сначала в профиле, а если там нет, то берёт стандартное)
     почту
     телефон
    :param user:
    :return: full_name, email, phone
    """
    full_name = user.profile.fullName
    if full_name is None or full_name.strip() == '':
        full_name = user.get_full_name()
    email = user.profile.email or ''
    phone = user.profile.phone or ''
    return full_name, email, phone


class PymentValidator:
    """
    Эмулятор оплаты.
    Обязательно нужно передать:
    order — сам заказ,
    number — номер карты,
    name — имя владельца карты,
    month — срок действия (месяц),
    year — срок действия (год),
    code — код с обратной стороны
    """
    order = None
    number = None
    name = None
    month = None
    year = None
    code = None

    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)
        self.__is_valid = False
        self.__messages_error = {'error': ''}
        self.__validate()

    @property
    def messages_error(self):
        return self.__messages_error

    @property
    def is_valid(self):
        return self.__is_valid

    def __set_is_valid(self, value):
        self.__is_valid = value

    def __set_messages_error(self, messages):
        self.__messages_error['error'] = messages

    def __validate(self):
        if not all([value for key, value in self.__dict__.items() if not key.startswith('_')]):
            self.__messages_error = {'error': 'Not all data available'}
        elif len(self.number) != 8 or (not self.number.isdigit()) or int(self.number) % 2 != 0:
            self.__set_messages_error('Invalid card number')
        elif len(self.code) != 3:
            self.__set_messages_error('Incorrect CVV code')
        elif (not self.month.isdigit()) or (not self.year.isdigit()):
            self.__set_messages_error('date must be a number')
        elif len(self.name.strip()) == 0:
            self.__set_messages_error('wrong name')
        try:
            year = self.year
            if len(year) == 2:
                year = int(year) + 2000
            target_date = date(
                year=int(year),
                month=int(self.month),
                day=monthrange(int(self.year), int(self.month))[1]
            )
            if target_date < datetime.now().date():
                self.__set_messages_error('The card has expired')
        except:
            self.__set_messages_error('wrong date')
        baskets = self.order.products
        for basket in baskets.all():
            if basket.count > basket.product.count:
                self.__set_messages_error('Not enough goods in stock')
                break
        if self.messages_error['error'] == '':
            self.__set_is_valid(True)


def get_no_img() -> str:
    """
    Функция вернёт адрес к изображению по умолчанию для продуктов не имеющих изображений
    :return:
    """
    return f'{MEDIA_URL}product/no_image/noimg.jpg'


def get_price_or_sale_price(instance: Product):
    """
    Функция принимает продукт, проверяет наличие акции и на основании этого возвращает его стоимость.
    :param instance:
    :return:
    """
    try:
        if instance.dateFrom.date() <= datetime.now().date() <= instance.dateTo.date():
            return instance.salePrice
    except:
        pass
    return instance.price
