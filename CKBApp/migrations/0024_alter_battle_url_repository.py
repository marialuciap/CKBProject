# Generated by Django 4.2.9 on 2024-02-04 00:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CKBApp', '0023_battle_url_repository'),
    ]

    operations = [
        migrations.AlterField(
            model_name='battle',
            name='url_repository',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
