# Generated by Django 4.2.6 on 2023-10-30 19:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopapp', '0024_alter_product_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='products', to='shopapp.tag'),
        ),
    ]
