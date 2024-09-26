# Generated by Django 4.2.6 on 2023-10-22 14:47

from django.db import migrations, models
import myprofile.models


class Migration(migrations.Migration):

    dependencies = [
        ('myprofile', '0003_alter_profile_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to=myprofile.models.avatar_directory_path),
        ),
    ]
