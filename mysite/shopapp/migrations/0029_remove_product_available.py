# Generated by Django 4.2.6 on 2023-11-02 06:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shopapp', '0028_reviews_author_auth_user_reviews_email_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='available',
        ),
    ]