# Generated by Django 4.2.9 on 2024-02-04 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CKBApp', '0024_alter_battle_url_repository'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='github_username',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
