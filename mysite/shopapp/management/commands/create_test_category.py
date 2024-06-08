from django.core.management import BaseCommand
import random
from shopapp.models import Category, SubCategory, Product, Reviews


class Command(BaseCommand):
    """
    Создаст категорию TestCategory,
     подкатегорию SubTestCategory и (в случайных вариантах) 100 продуктов и отзывов к этим продуктам.
    """

    def handle(self, *args, **options):
        category, created = Category.objects.get_or_create(
            title='TestCategory'
        )
        if not created:
            print('**** A set of test categories and products has already been created ****')
            return
        subcategory = SubCategory.objects.create(
            title='SubTestCategory',
            category=category
        )

        for i in range(1, 101):
            freedelivery = True if random.randint(0, 1) == 1 else False
            product = Product.objects.create(
                category=subcategory,
                price=random.randint(1, 3000),
                count=random.randint(0, 10),
                title=f'test{i}',
                description=f'good product test{i}',
                fullDescription=f'very good product test{i}',
                freeDelivery=freedelivery
            )

            for ind in range(1, random.randint(1, 21)):
                Reviews.objects.create(
                    author=f'author{ind}',
                    email=f'author{ind}@skillbox.ru',
                    product_review=product,
                    text='Product received',
                    rate=random.randint(1, 5)
                )
        print('ok')
