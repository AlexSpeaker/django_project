from datetime import datetime

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Avg
from django.utils.translation import gettext_lazy as _


def product_image_directory_path(instance: 'ProductImage', filename: str) -> str:
    """
    Генератор относительного пути для сохранения файла изображения для модели Product
    :param instance:
    :param filename:
    :return:
    """
    return 'product/{product_id}/image/{filename}'.format(
        product_id=instance.product.pk,
        filename=filename
    )


def category_image_directory_path(instance: 'Category', filename: str) -> str:
    """
    Генератор относительного пути для сохранения файла изображения для модели Category
    :param instance:
    :param filename:
    :return:
    """
    return 'category/{category_id}/image/{filename}'.format(
        category_id=instance.pk,
        filename=filename
    )


def subcategory_image_directory_path(instance: 'SubCategory', filename: str) -> str:
    """
    Генератор относительного пути для сохранения файла изображения для модели Subcategory
    :param instance:
    :param filename:
    :return:
    """
    return 'subcategory/{subcategory_id}/image/{filename}'.format(
        subcategory_id=instance.pk,
        filename=filename
    )


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self) -> str:
        return f"{self.name.title()}"

    class Meta:
        ordering = ['name']


class Category(models.Model):
    title = models.CharField(max_length=100, blank=False, null=False, unique=True)
    image = models.ImageField(null=True, blank=True, upload_to=category_image_directory_path, default=None)

    def __str__(self) -> str:
        return f"{self.title.title()}"

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ['title']


class SubCategory(models.Model):
    title = models.CharField(max_length=100, blank=False, null=False, unique=True)
    category = models.ForeignKey(Category, related_name="subcategories", on_delete=models.PROTECT)
    image = models.ImageField(null=True, blank=True, upload_to=subcategory_image_directory_path, default=None)

    def __str__(self) -> str:
        return f"{self.title.title()}"

    class Meta:
        verbose_name = _("SubCategory")
        verbose_name_plural = _("SubCategories")
        ordering = ['title']


class Product(models.Model):
    category = models.ForeignKey(
        SubCategory,
        on_delete=models.PROTECT,
        related_name="products_category",
        blank=False,
        null=False
    )
    price = models.DecimalField(
        default=0,
        max_digits=8,
        decimal_places=2,
        blank=False,
        null=False
    )
    count = models.PositiveSmallIntegerField(default=0, blank=False, null=False)
    date = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=200, blank=False, null=False, unique=True)
    description = models.TextField(max_length=1000, blank=True, null=True)
    fullDescription = models.TextField(max_length=5000, blank=True, null=True)
    freeDelivery = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag, related_name="products", blank=True)
    rating = models.DecimalField(
        null=True,
        default=None,
        max_digits=2,
        decimal_places=1,
        validators=[
            MaxValueValidator(5),
            MinValueValidator(0)
        ]
    )
    discount = models.DecimalField(
        default=0,
        max_digits=4,
        decimal_places=1,
        validators=[
            MaxValueValidator(100),
            MinValueValidator(0)
        ]
    )
    salePrice = models.DecimalField(
        default=0,
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True
    )
    dateFrom = models.DateTimeField(null=True, blank=True)
    dateTo = models.DateTimeField(null=True, blank=True)

    def save(
            self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        try:
            if self.dateFrom.date() <= datetime.now().date() <= self.dateTo.date():
                self.salePrice = round((self.price - (self.price * self.discount) / 100), 1)
            else:
                self.salePrice = None
        except:
            self.salePrice = None
        super().save()

    def __str__(self) -> str:
        return f"{self.title.title()}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=product_image_directory_path)


def set_average_rating(product_pk: int) -> None:
    """
    Функция делает перерасчёт среднего рейтинга продукта при сохранении или удалении отзыва на этот продукт
    :param product_pk:
    :return:
    """
    product = Product.objects.prefetch_related('reviews').get(pk=product_pk)
    product.rating = product.reviews.aggregate(Avg('rate'))['rate__avg']
    product.save()


class Reviews(models.Model):
    author_auth_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author_reviews',
        blank=True,
        null=True
    )
    author = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    product_review = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField(blank=True, max_length=2000)
    rate = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )
    date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Review")
        verbose_name_plural = _("Reviews")
        ordering = ['-date']

    def save(
            self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        super().save()
        set_average_rating(self.product_review.pk)

    def delete(self, using=None, keep_parents=False):
        super().delete()
        set_average_rating(self.product_review.pk)


class Specification(models.Model):
    product = models.ForeignKey(Product, related_name="specifications", on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=False, null=False)
    value = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f"{self.name.title()}"


class DeliveryType(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    delivery_price = models.DecimalField(
        null=False,
        blank=False,
        default=0,
        max_digits=6,
        decimal_places=2,
    )
    free_shipping_on_price = models.DecimalField(
        null=True,
        blank=True,
        default=None,
        max_digits=6,
        decimal_places=2,
    )

    def __str__(self) -> str:
        return f"{self.name.title()}"


class Order(models.Model):
    user_auth_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        default=None
    )
    user = models.CharField(max_length=100, blank=True, null=True, default=None)
    createdAt = models.DateTimeField(auto_now=True)
    fullName = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=17, blank=True, null=True)
    deliveryType = models.CharField(max_length=10, default='ordinary')
    paymentType = models.CharField(max_length=10, default='online')
    totalCost = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(0)
        ]
    )
    status = models.CharField(max_length=30)
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)


class Basket(models.Model):
    user_auth_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        default=None
    )
    user = models.CharField(max_length=100, blank=True, null=True, default=None)
    created_at = models.DateTimeField(auto_now=True)
    product = models.ForeignKey(Product, related_name="baskets", on_delete=models.CASCADE)
    count = models.PositiveSmallIntegerField(
        default=0,
        blank=False,
        null=False
    )
    order = models.ForeignKey(
        Order,
        null=True,
        blank=True,
        related_name='products',
        on_delete=models.CASCADE,
    )
    archived = models.BooleanField(default=False)
