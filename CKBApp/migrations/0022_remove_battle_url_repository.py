# Generated by Django 4.2.9 on 2024-02-03 23:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CKBApp', '0021_battle_url_repository'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='battle',
            name='url_repository',
        ),
    ]