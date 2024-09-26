import operator
import random
from datetime import datetime
from functools import reduce

from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Product, Tag, Basket, Order
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    TagSerializer,
    ReviewsSerializer,
    BasketSerializer,
    OrderSerializer, SaleProductSerializer
)
from .services import (
    get_popular_tags,
    get_filter_param,
    get_user_param_no_create_token,
    get_user_param_create_token,
    get_fullname_email_phone, PymentValidator, get_price_or_sale_price,
)


class CategoryAPIView(APIView):
    queryset = Category.objects.prefetch_related('subcategories')
    serializer_class = CategorySerializer

    def get(self, request: Request, *args, **kwargs) -> Response:
        response_data = self.serializer_class(self.queryset.all(), many=True)
        return Response(response_data.data)


class ProductAPIView(APIView):
    queryset = (
        Product.objects.select_related('category').
        prefetch_related(
            'tags',
            'images',
            'specifications',
            'reviews',
            'reviews__author_auth_user'
        )
    )
    serializer_class = ProductSerializer

    def get(self, request: Request, *args, **kwargs) -> Response:
        product_pk = kwargs['id']
        product = get_object_or_404(self.queryset, pk=product_pk)
        response_data = self.serializer_class(product)
        return Response(response_data.data)


class TagsCategoryAPIView(APIView):
    serializer_class = TagSerializer
    queryset = Tag.objects.prefetch_related('products')

    def get(self, request: Request, *args, **kwargs) -> Response:
        category_pk = request.GET.get('category')
        if category_pk:
            if int(category_pk) // 10e6:
                queryset = self.queryset.filter(products__category__category=int(category_pk) % 10e6)
            else:
                queryset = self.queryset.filter(products__category=category_pk)
        else:
            queryset = self.queryset.all()
        serializer_data = self.serializer_class(queryset, many=True, read_only=True)
        if serializer_data:
            response_data = get_popular_tags(serializer_data.data)
            return Response(response_data)
        return Response(status=status.HTTP_200_OK)


class CatalogAPIView(APIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.select_related('category').prefetch_related('tags', 'images', 'reviews')

    def get(self, request: Request, *args, **kwargs) -> Response:
        data_request = request.GET

        filter_param = get_filter_param(data_request)

        current_page = data_request.get('currentPage', 1)
        limit = data_request.get('limit', 20)

        sort = data_request.get('sort', 'date')
        sort = 'reviews_all' if sort == 'reviews' else sort
        sort_type = data_request.get('sortType', 'dec')
        sort = f"-{sort}" if sort_type == 'dec' else sort

        products = self.queryset.annotate(reviews_all=Count('reviews')).filter(
            reduce(operator.and_, filter_param)
        ).order_by(sort)

        paginator = Paginator(products, limit)
        page_odj = paginator.get_page(current_page)

        serializer_data = self.serializer_class(page_odj, many=True, read_only=True, context={'short': True})
        data = dict(
            items=serializer_data.data,
            currentPage=current_page,
            lastPage=paginator.page_range[-1]
        )
        return Response(data=data)


class ProductReviewAPIView(APIView):
    serializer_class = ReviewsSerializer
    queryset = Product.objects.prefetch_related('reviews', 'reviews__author_auth_user')

    def post(self, request: Request, *args, **kwargs) -> Response:
        user = request.user
        data = request.data
        product_pk = kwargs['id']
        product = get_object_or_404(self.queryset, pk=product_pk)
        if not user.is_authenticated:
            user = None
        data['author_auth_user'] = user
        data['product_review'] = product
        if data['author'].strip() == '':
            data['author'] = 'Anonymous'
        review_serializer = self.serializer_class(data=data)
        if not review_serializer.is_valid():
            message_error = {'error': 'Incorrect data'}
            return Response(data=message_error, status=status.HTTP_400_BAD_REQUEST)
        review = review_serializer.create(data)
        product.reviews.add(review)
        response_data = self.serializer_class(instance=product.reviews, many=True, read_only=True)
        return Response(response_data.data)


class ProductPopularAPIView(APIView):
    queryset = Product.objects.prefetch_related('tags', 'images', 'reviews', 'specifications')
    serializer_class = ProductSerializer

    def get(self, request: Request, *args, **kwargs) -> Response:
        products = self.queryset.filter(count__gt=0).order_by('-rating')[:4]
        serializer_data = self.serializer_class(products, many=True, context={'short': True})
        return Response(serializer_data.data)


class ProductLimitedAPIView(APIView):
    queryset = Product.objects.prefetch_related('tags', 'images', 'reviews', 'specifications')
    serializer_class = ProductSerializer

    def get(self, request: Request, *args, **kwargs) -> Response:
        products = self.queryset.filter(count__range=[1, 5]).order_by('count')
        paginator = Paginator(products, 4)
        list_page = list(paginator.page_range)
        current_page = random.randint(list_page[0], list_page[-1])
        page_odj = paginator.get_page(current_page)
        serializer_data = self.serializer_class(page_odj, many=True, context={'short': True})
        return Response(serializer_data.data)


class BasketAPIView(APIView):
    queryset = Basket.objects.prefetch_related(
        'product__reviews',
        'product__tags',
        'product__images',
        'product__specifications'
    )
    serializer_class = BasketSerializer

    def get(self, request: Request, *args, **kwargs) -> Response:
        user_param = get_user_param_no_create_token(request)
        if user_param is None:
            return Response(status=status.HTTP_200_OK)
        baskets = self.queryset.filter(Q(archived=False) & Q(**user_param))
        for basket in baskets:
            if basket.product.count == 0:
                basket.delete()
            elif basket.product.count < basket.count:
                basket.count = basket.product.count
                basket.save()
        response = self.serializer_class(baskets, many=True).data
        return Response(response)

    def post(self, request: Request, *args, **kwargs) -> Response:
        user_param = get_user_param_create_token(request)
        product_id = request.data['id']
        count = request.data['count']
        product = get_object_or_404(Product, pk=product_id)
        if int(product.count) > 0:
            basket, created = Basket.objects.get_or_create(product=product, archived=False, **user_param)
            new_count = int(basket.count) + int(count)
            if int(product.count) >= new_count > 0:
                basket.count = new_count
            elif new_count > int(product.count):
                basket.count = product.count
            else:
                basket.count = 1
            basket.save()
        else:
            message_error = {'error': 'Out of products'}
            return Response(data=message_error, status=status.HTTP_400_BAD_REQUEST)
        baskets = self.queryset.filter(Q(archived=False) & Q(**user_param))
        response = self.serializer_class(baskets, many=True).data

        return Response(response)

    def delete(self, request: Request, *args, **kwargs) -> Response:
        user_param = get_user_param_no_create_token(request)
        if user_param is None:
            message_error = {'error': 'Incorrect data'}
            return Response(data=message_error, status=status.HTTP_400_BAD_REQUEST)
        product_id = request.data['id']
        count = request.data['count']
        product = get_object_or_404(Product, pk=product_id)
        basket = get_object_or_404(Basket, product=product, archived=False, **user_param)
        new_count = int(basket.count) - int(count)
        if new_count <= 0:
            basket.delete()
        else:
            basket.count = new_count
            basket.save()
        baskets = self.queryset.filter(Q(archived=False) & Q(**user_param))
        response = self.serializer_class(baskets, many=True).data
        return Response(response)


class OrdersAPIView(APIView):
    order_queryset = (
        Order.objects.
        select_related(
            'user_auth_user__profile',
        ).
        prefetch_related(
            'products__product__tags',
            'products__product__images',
            'products__product__reviews',
            'products__product__specifications'
        )
    )
    basket_queryset = Basket.objects.prefetch_related(
        'product__reviews',
        'product__tags',
        'product__images',
        'product__specifications'
    )
    serializer_class = OrderSerializer

    def get(self, request: Request, *args, **kwargs) -> Response:
        user_param = get_user_param_no_create_token(request)
        if not user_param:
            return Response(status=status.HTTP_200_OK)
        orders = self.order_queryset.filter(**user_param)
        response = self.serializer_class(orders, many=True).data
        return Response(response)

    def post(self, request: Request, *args, **kwargs) -> Response:
        user_param = get_user_param_no_create_token(request)
        if user_param is None:
            message_error = {'error': 'Incorrect data'}
            return Response(data=message_error, status=status.HTTP_400_BAD_REQUEST)
        baskets = self.basket_queryset.filter(Q(archived=False) & Q(**user_param))
        if not baskets:
            message_error = {'error': 'Incorrect data'}
            return Response(data=message_error, status=status.HTTP_400_BAD_REQUEST)
        user = user_param.get('user_auth_user')

        if user:
            full_name, email, phone = get_fullname_email_phone(user)
        else:
            full_name, email, phone = '', '', ''
        data_order = {
            'fullName': full_name,
            'email': email,
            'phone': phone
        }
        total_cost = round(sum([
            float(get_price_or_sale_price(basket.product)) * int(basket.count)
            for basket in baskets
        ]), 1)
        order = Order.objects.create(status='created', totalCost=total_cost, **data_order, **user_param)
        baskets.update(archived=True, order=order)
        response_id = dict(orderId=order.pk)
        return Response(response_id)


class OrderAPIView(APIView):
    queryset = (
        Order.objects.
        select_related(
            'user_auth_user__profile',
        ).
        prefetch_related(
            'products__product__tags',
            'products__product__images',
            'products__product__reviews',
            'products__product__specifications'
        )
    )
    serializer_class = OrderSerializer

    def get(self, request: Request, *args, **kwargs) -> Response:
        id_order = kwargs.get('id')
        user = request.user
        user_param = get_user_param_no_create_token(request)
        if not user_param:
            message_error = {'error': 'Incorrect data'}
            return Response(data=message_error, status=status.HTTP_400_BAD_REQUEST)
        order = get_object_or_404(self.queryset, pk=id_order, **user_param)
        response_order = self.serializer_class(order)
        if (user.is_authenticated and
                (response_order.data['fullName'] is None or response_order.data['fullName'].strip() == '')):
            full_name, email, phone = get_fullname_email_phone(user)
            data_order = {
                'fullName': full_name,
                'email': email,
                'phone': phone
            }
            order = response_order.update(order, data_order)
            response_order = self.serializer_class(order)
        return Response(response_order.data)

    def post(self, request: Request, *args, **kwargs) -> Response:
        id_order = kwargs.get('id')
        user_param = get_user_param_no_create_token(request)
        if not user_param:
            message_error = {'error': 'Incorrect data'}
            return Response(data=message_error, status=status.HTTP_400_BAD_REQUEST)
        order = get_object_or_404(self.queryset, pk=id_order, **user_param)
        order_data = {
            'fullName': request.data.get('fullName'),
            'email': request.data.get('email'),
            'phone': request.data.get('phone'),
            'deliveryType': request.data.get('deliveryType'),
            'paymentType': request.data.get('paymentType'),
            'city': request.data.get('city'),
            'address': request.data.get('address'),
            'status': 'confirmed'
        }
        order_serializer = self.serializer_class(data=order_data, instance=order)
        if order_serializer.is_valid():
            order.totalCost = round(sum([
                float(get_price_or_sale_price(basket.product)) * int(basket.count)
                for basket in order.products.all()
            ]), 1)
            order = order_serializer.update(order, order_data)
            order_data = {'orderId': order.pk}
        else:
            message_error = {'error': 'Incorrect data'}
            return Response(data=message_error, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK, data=order_data)


class PaymentAPIView(APIView):
    queryset = (
        Order.objects.
        select_related(
            'user_auth_user',
            'user_auth_user__profile',
        ).
        prefetch_related(
            'products__product__tags',
            'products__product__images',
            'products__product__reviews',
            'products__product__specifications'
        )
    )
    product_serializer_class = ProductSerializer

    def post(self, request: Request, *args, **kwargs) -> Response:
        order_pk = kwargs.get('id')
        user_param = get_user_param_no_create_token(request)
        if not user_param:
            message_error = {'error': 'Incorrect data'}
            return Response(data=message_error, status=status.HTTP_400_BAD_REQUEST)
        order = get_object_or_404(self.queryset, pk=order_pk, **user_param)
        pyment = PymentValidator(order=order, **request.data)
        if pyment.is_valid:
            baskets = order.products
            products_list = []
            for basket in baskets.all():
                product = basket.product
                product.count -= basket.count
                products_list.append(product)
            Product.objects.bulk_update(products_list, fields=['count'])
            order.status = 'paid'
            order.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=pyment.messages_error)


class SalesAPIView(APIView):
    queryset = (
        Product.objects.select_related('category').
        prefetch_related(
            'tags',
            'images',
            'specifications',
            'reviews',
        )
    )
    serializer_class = SaleProductSerializer

    def get(self, request: Request, *args, **kwargs) -> Response:
        current_page = request.GET.get('currentPage')
        date_now = datetime.now()
        products = self.queryset.filter(Q(dateFrom__lte=date_now) & Q(dateTo__gte=date_now) & Q(count__gt=0))
        paginator = Paginator(products, 10)
        page_odj = paginator.get_page(current_page)
        products_data = self.serializer_class(page_odj, many=True).data
        data = dict(
            items=products_data,
            currentPage=int(current_page),
            lastPage=paginator.page_range[-1]
        )
        return Response(data)


class BannersAPIView(APIView):
    queryset = (
        Product.objects.select_related('category').
        prefetch_related(
            'tags',
            'images',
            'specifications',
            'reviews',
        )
    )
    serializer_class = ProductSerializer

    def get(self, request: Request, *args, **kwargs) -> Response:
        count_products = self.queryset.count()
        selected_numbers = random.sample(range(0, count_products - 1), k=3)
        products = tuple(self.queryset.all()[i] for i in selected_numbers)
        serializer_data = self.serializer_class(products, many=True, context={'short': True})
        return Response(serializer_data.data)
