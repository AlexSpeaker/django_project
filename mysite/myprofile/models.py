from django.contrib.auth.models import User
from django.db import models


def avatar_directory_path(instance: 'Profile', filename: str) -> str:
    """
    Генератор относительного пути для сохранения файла изображения для модели Profile
    :param instance:
    :param filename:
    :return:
    """
    return 'profile/{user_id}/avatar/{filename}'.format(
        user_id=instance.user.pk,
        filename=filename
    )


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    fullName = models.CharField(max_length=100, blank=True, default="")
    email = models.EmailField(max_length=70, unique=True, default=None, null=True)
    phone = models.CharField(max_length=17, unique=True, default=None, null=True)
    avatar = models.ImageField(null=True, blank=True, upload_to=avatar_directory_path, default=None)
