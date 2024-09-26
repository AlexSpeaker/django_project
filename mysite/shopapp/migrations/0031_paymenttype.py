# Generated by Django 4.2.6 on 2023-11-03 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopapp', '0030_deliverytype'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('value', models.CharField(default=('my', 'stranger'), max_length=100)),
            ],
        ),
    ]
