# Generated by Django 4.2.9 on 2024-02-03 23:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CKBApp', '0022_remove_battle_url_repository'),
    ]

    operations = [
        migrations.AddField(
            model_name='battle',
            name='url_repository',
            field=models.CharField(default=None, max_length=100),
        ),
    ]
