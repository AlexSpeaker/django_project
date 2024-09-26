from rest_framework import serializers
from .models import Category, SubCategory, Product, Reviews, Tag, Specification, Basket, Order, ProductImage
from .services import get_no_img, get_price_or_sale_price


class SubCategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = SubCategory
        fields = 'id', 'title', 'image'

    @classmethod
    def get_image(cls, instance):
        data = dict(src=get_no_img(), alt='No Image')
        if instance.image:
            data['src'] = instance.image.url
        return data


class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubCategorySerializer(read_only=True, many=True)
    image = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = 'id', 'title', 'image', 'subcategories'

    @classmethod
    def get_image(cls, instance: Category):
        data = dict(src=get_no_img(), alt='No Image')
        if instance.image:
            data['src'] = instance.image.url
        return data

    @classmethod
    def get_id(cls, instance: Category):
        return instance.id + 10e6


class ReviewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reviews
        fields = (
            'author',
            'email',
            'text',
            'rate',
            'date'
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name'
        )


class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = (
            'name',
            'value'
        )


class ProductImageSerializer(serializers.ModelSerializer):
    src = serializers.CharField(source='image.url')
    alt = serializers.CharField(default='No Image')

    class Meta:
        model = ProductImage
        fields = (
            'src',
            'alt'
        )


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(read_only=True, many=True)
    tags = TagSerializer(read_only=True, many=True)
    reviews = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'category',
            'price',
            'count',
            'date',
            'title',
            'description',
            'freeDelivery',
            'images',
            'reviews',
            'tags',
            'rating'
        ]

    @classmethod
    def get_price(cls, instance: Product):
        return get_price_or_sale_price(instance)

    def get_fields(self):
        fields = super().get_fields()
        product_short = self.context.get('short', False)
        if not product_short:
            fields['specifications'] = serializers.SerializerMethodField()
        return fields

    def get_field_names(self, declared_fields, info):
        fields = super().get_field_names(declared_fields, info)
        product_short = self.context.get('short', False)
        if not product_short:
            fields.extend([
                'fullDescription',
                'specifications',
            ])
        return fields

    def get_reviews(self, instance: Product):
        product_short = self.context.get('short', False)
        if not product_short:
            return ReviewsSerializer(read_only=True, many=True, instance=instance.reviews).data
        return instance.reviews.count()

    @classmethod
    def get_specifications(cls, instance: Product):
        return SpecificationSerializer(read_only=True, many=True, instance=instance.specifications).data

    def to_representation(self, instance: Product):
        data = super().to_representation(instance)
        if len(data['images']) == 0:
            data['images'] = [
                dict(src=get_no_img(), alt='No Image')
            ]
        return data


class BasketSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()

    class Meta:
        model = Basket
        fields = (
            'product',
        )

    @classmethod
    def get_product(cls, instance: Basket):
        product = ProductSerializer(
            read_only=True,
            context={'short': True},
            instance=instance.product
        )
        data = product.data
        data['count'] = instance.count
        return data

    def to_representation(self, instance: Product):
        data = super().to_representation(instance)

        return data['product']


class OrderSerializer(serializers.ModelSerializer):
    products = BasketSerializer(read_only=True, many=True)
    createdAt = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'id',
            'createdAt',
            'fullName',
            'email',
            'phone',
            'deliveryType',
            'paymentType',
            'totalCost',
            'status',
            'city',
            'address',
            'products'
        )

    @classmethod
    def get_createdAt(cls, instance: Order):
        return instance.createdAt.strftime("%d.%m.%Y %H:%M")


class SaleProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(read_only=True, many=True)
    dateFrom = serializers.SerializerMethodField()
    dateTo = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'price',
            'salePrice',
            'dateFrom',
            'dateTo',
            'title',
            'images',
        ]

    @classmethod
    def get_dateFrom(cls, instance: Product):
        return instance.dateFrom.strftime("%d-%m")

    @classmethod
    def get_dateTo(cls, instance: Product):
        return instance.dateTo.strftime("%d-%m")

    def to_representation(self, instance: Product):
        data = super().to_representation(instance)
        if len(data['images']) == 0:
            data['images'] = [
                dict(src=get_no_img(), alt='No Image')
            ]
        return data
