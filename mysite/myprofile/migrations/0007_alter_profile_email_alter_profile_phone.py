# Generated by Django 4.2.6 on 2023-10-23 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myprofile', '0006_alter_profile_email_alter_profile_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='email',
            field=models.EmailField(blank=True, default=None, max_length=70, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='phone',
            field=models.CharField(blank=True, default=None, max_length=17, null=True, unique=True),
        ),
    ]
