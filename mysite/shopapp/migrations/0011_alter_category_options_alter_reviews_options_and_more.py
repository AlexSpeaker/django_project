# Generated by Django 4.2.6 on 2023-10-28 18:25

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import shopapp.models


class Migration(migrations.Migration):

    dependencies = [
        ('shopapp', '0010_alter_product_description_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['title'], 'verbose_name': 'Category', 'verbose_name_plural': 'Categories'},
        ),
        migrations.AlterModelOptions(
            name='reviews',
            options={'ordering': ['-date'], 'verbose_name': 'Review', 'verbose_name_plural': 'Reviews'},
        ),
        migrations.AlterModelOptions(
            name='subcategory',
            options={'ordering': ['title'], 'verbose_name': 'SubCategory', 'verbose_name_plural': 'SubCategories'},
        ),
        migrations.RenameField(
            model_name='category',
            old_name='name',
            new_name='title',
        ),
        migrations.RenameField(
            model_name='subcategory',
            old_name='name',
            new_name='title',
        ),
        migrations.AddField(
            model_name='category',
            name='image',
            field=models.ImageField(blank=True, default=None, null=True, upload_to=shopapp.models.category_image_directory_path),
        ),
        migrations.AddField(
            model_name='subcategory',
            name='image',
            field=models.ImageField(blank=True, default=None, null=True, upload_to=shopapp.models.subcategory_image_directory_path),
        ),
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='shopapp.subcategory'),
        ),
        migrations.AlterField(
            model_name='product',
            name='rating',
            field=models.DecimalField(decimal_places=1, default=None, max_digits=2, null=True, validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='product',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='tags', to='shopapp.tag'),
        ),
        migrations.AlterField(
            model_name='reviews',
            name='rate',
            field=models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]),
        ),
    ]