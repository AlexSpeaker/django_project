# Generated by Django 4.2.6 on 2023-10-29 13:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopapp', '0023_alter_reviews_product_review'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='title',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]
