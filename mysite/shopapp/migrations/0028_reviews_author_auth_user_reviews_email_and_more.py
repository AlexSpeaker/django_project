# Generated by Django 4.2.6 on 2023-11-01 17:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shopapp', '0027_product_available'),
    ]

    operations = [
        migrations.AddField(
            model_name='reviews',
            name='author_auth_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='author_reviews', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='reviews',
            name='email',
            field=models.EmailField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='reviews',
            name='author',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]