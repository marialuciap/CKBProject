# Generated by Django 4.2.9 on 2024-02-03 23:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CKBApp', '0020_battle_repository_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='battle',
            name='url_repository',
            field=models.CharField(default=None, max_length=100),
        ),
    ]
