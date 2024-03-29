# Generated by Django 4.2.9 on 2024-01-31 17:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('CKBApp', '0004_team_creator'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invite',
            name='user_invited',
            field=models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, related_name='invites_received', to='CKBApp.user'),
        ),
        migrations.AlterField(
            model_name='invite',
            name='user_who_invite',
            field=models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, related_name='invites_sent', to='CKBApp.user'),
        ),
        migrations.AlterField(
            model_name='team',
            name='creator',
            field=models.OneToOneField(blank=True, default=None, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
    ]
