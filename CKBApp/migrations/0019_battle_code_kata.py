# Generated by Django 4.2.9 on 2024-02-03 21:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CKBApp', '0018_battle_manually_evaluated'),
    ]

    operations = [
        migrations.AddField(
            model_name='battle',
            name='code_kata',
            field=models.FileField(default=None, upload_to='media/'),
        ),
    ]
