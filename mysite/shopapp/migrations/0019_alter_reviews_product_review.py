# Generated by Django 4.2.6 on 2023-10-29 12:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shopapp', '0018_alter_reviews_product_review'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reviews',
            name='product_review',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shopapp.product'),
        ),
    ]
