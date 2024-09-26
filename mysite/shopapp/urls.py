from django.urls import path

from .viewsapi import (
    CategoryAPIView,
    ProductAPIView,
    TagsCategoryAPIView,
    CatalogAPIView,
    ProductReviewAPIView,
    ProductPopularAPIView,
    ProductLimitedAPIView,
    BasketAPIView,
    OrdersAPIView,
    OrderAPIView,
    PaymentAPIView, SalesAPIView, BannersAPIView
)

app_name = "shopapp"

urlpatterns = [
    path('api/categories', CategoryAPIView.as_view(), name='category-api'),
    path('api/products/popular/', ProductPopularAPIView.as_view(), name='product-popular-api'),
    path('api/products/limited/', ProductLimitedAPIView.as_view(), name='product-limited-api'),
    path('api/tags', TagsCategoryAPIView.as_view(), name='tags-api'),
    path('api/catalog', CatalogAPIView.as_view(), name='catalog-api'),
    path('api/basket', BasketAPIView.as_view(), name='basket-api'),
    path('api/orders', OrdersAPIView.as_view(), name='orders-api'),
    path('api/sales', SalesAPIView.as_view(), name='sales-api'),
    path('api/banners', BannersAPIView.as_view(), name='banners-api'),
    path('api/order/<int:id>', OrderAPIView.as_view(), name='order-id-api'),
    path('api/payment/<int:id>', PaymentAPIView.as_view(), name='payment-api'),
    path('api/product/<int:id>', ProductAPIView.as_view(), name='product-api'),
    path('api/product/<int:id>/reviews', ProductReviewAPIView.as_view(), name='product-review-api'),
]
