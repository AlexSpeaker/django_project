from django.core.management import BaseCommand

from shopapp.models import Product, SubCategory, Category


class Command(BaseCommand):
    """
    Удалит категорию TestCategory, подкатегорию SubTestCategory и их продукты с отзывами
    """
    def handle(self, *args, **options):
        products = Product.objects.select_related('category').filter(category__title='SubTestCategory')
        if not products:
            print('**** No test products found ****')
        else:
            products.delete()
            print('products -> ok')
        subcategory = SubCategory.objects.select_related('category').get(title='SubTestCategory')
        if not subcategory:
            print('**** No test subcategory found ****')
        else:
            subcategory.delete()
            print('subcategory -> ok')
        category = Category.objects.get(title='TestCategory')
        if not category:
            print('**** No test category found ****')
        else:
            category.delete()
            print('category -> ok')
