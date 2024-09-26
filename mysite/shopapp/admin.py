import textwrap
from django.contrib import messages
from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Category, SubCategory, Product, Tag, ProductImage, Specification, Reviews, Order, Basket


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    readonly_fields = ['img_preview']
    classes = ['collapse']

    @classmethod
    def img_preview(cls, obj: ProductImage):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="25">')


class SubCategoryInline(admin.TabularInline):
    model = SubCategory
    readonly_fields = ['img_preview']

    @classmethod
    def img_preview(cls, obj: SubCategory):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="25">')


class SpecificationInline(admin.TabularInline):
    model = Specification
    classes = ['collapse']


class BasketsInline(admin.TabularInline):
    model = Basket
    fields = ['product', 'count']
    readonly_fields = fields
    max_num = 0
    classes = ['collapse']


class ReviewsInline(admin.TabularInline):
    model = Reviews
    fields = ['author_auth_user', 'author', 'rate', 'text', 'date']
    readonly_fields = ['author_auth_user', 'author', 'rate', 'text', 'date']
    max_num = 0
    classes = ['collapse']


class ProductInline(admin.TabularInline):
    model = Product
    fields = ['title', 'price', 'description', 'count', 'date', 'rating']
    readonly_fields = ['title', 'price', 'description', 'count', 'date', 'rating']
    max_num = 0
    classes = ['collapse']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["pk", "title", "list_of_subcategory", 'img_preview']
    list_display_links = ["pk", "title"]
    readonly_fields = ['img_preview']
    search_fields = ["title"]
    inlines = [
        SubCategoryInline
    ]

    @classmethod
    def img_preview(cls, obj: Category):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="25">')

    def get_queryset(self, request):
        return Category.objects.prefetch_related('subcategories')

    @classmethod
    def list_of_subcategory(cls, obj: Category) -> str:
        return ", ".join([subcategory.title for subcategory in obj.subcategories.all()])

    def save_model(self, request, obj: Category, form, change):
        if not change:
            image = obj.image
            obj.image = None
            obj.save()
            obj.image = image
        obj.save()

    def delete_model(self, request, obj):
        messages.set_level(request, messages.ERROR)
        message = "Не стоит удалять категорию. Но если сильно хочется, то воспользуйтесь полем 'actions'"
        self.message_user(request, message, level=messages.ERROR)


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_filter = [
        'category__title',
    ]
    inlines = [
        ProductInline,
    ]
    list_display = ["pk", "title", "category", 'img_preview']
    list_display_links = ["pk", "title"]
    readonly_fields = ['img_preview']
    search_fields = ["title"]

    @classmethod
    def img_preview(cls, obj: SubCategory):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="25">')

    def get_queryset(self, request):
        return SubCategory.objects.select_related('category').prefetch_related('products_category')

    def save_model(self, request, obj: SubCategory, form, change):
        if not change:
            image = obj.image
            obj.image = None
            obj.save()
            obj.image = image
        obj.save()

    def delete_model(self, request, obj):
        messages.set_level(request, messages.ERROR)
        message = "Не стоит удалять подкатегорию. Но если сильно хочется, то воспользуйтесь полем 'actions'"
        self.message_user(request, message, level=messages.ERROR)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    filter_horizontal = ('tags',)
    list_per_page = 10
    list_filter = [
        'category',
    ]
    inlines = [
        SpecificationInline,
        ProductImageInline,
        ReviewsInline
    ]
    search_fields = ["title"]
    list_display = [
        'pk',
        'title',
        'category',
        'price',
        'discount',
        'salePrice',
        'dateFrom',
        'dateTo',
        'count',
        'date',
        'freeDelivery',
        'rating',
    ]
    list_display_links = ["pk", "title"]
    fields = [
        'title',
        'category',
        'price',
        'discount',
        'salePrice',
        'dateFrom',
        'dateTo',
        'description',
        'fullDescription',
        'count',
        'freeDelivery',
        'tags',
    ]
    readonly_fields = ['salePrice',]

    def get_queryset(self, request):
        return (
            Product.objects.
            select_related('category').
            prefetch_related(
                'tags',
                'images',
                'specifications',
                'reviews',
                'reviews__author_auth_user'
            )
        )


@admin.register(Reviews)
class ReviewsAdmin(admin.ModelAdmin):
    list_per_page = 10
    search_fields = ["author", "product_review__title"]
    list_display = [
        'pk',
        'author',
        'product_review',
        'rate',
        'text_short',
        'date'
    ]
    list_display_links = ["pk", "author", 'product_review']
    readonly_fields = ['author', 'email', 'rate', 'text', 'date', 'product_review']

    def get_queryset(self, request):
        return Reviews.objects.prefetch_related('product_review')

    @classmethod
    def text_short(cls, obj: Reviews):
        return textwrap.shorten(obj.text, width=50, placeholder=" ...")

    def has_add_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        messages.set_level(request, messages.ERROR)
        message = "Невозможно создать отзыв через админ-панель."
        self.message_user(request, message, level=messages.ERROR)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = [
        'pk',
        'name'
    ]
    list_display_links = ["pk", "name"]
    fields = [
        'name',
    ]

    def save_model(self, request, obj: Tag, form, change):
        obj.name = obj.name.lower().strip()
        obj.save()

    def delete_model(self, request, obj):
        messages.set_level(request, messages.ERROR)
        message = "Не стоит удалять теги. Но если сильно хочется, то воспользуйтесь полем 'actions'"
        self.message_user(request, message, level=messages.ERROR)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_per_page = 10
    inlines = [
        BasketsInline,
    ]
    list_display = [
        'pk',
        'user_auth_user',
        'fullName',
        'createdAt',
        'totalCost',
        'status'
    ]
    list_display_links = ["pk", "user_auth_user", "fullName"]
    readonly_fields = (
        'user_auth_user',
        'createdAt',
        'fullName',
        'email',
        'phone',
        'deliveryType',
        'paymentType',
        'totalCost',
        'status',
        'city',
        'address'
    )
    fields = readonly_fields

    def has_add_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        queryset = (
            Order.objects.
            select_related(
                'user_auth_user',
                'user_auth_user__profile',
            ).
            prefetch_related(
                'products',
                'products__product',
                'products__product__tags',
                'products__product__images',
                'products__product__reviews'
            )
        )
        return queryset
