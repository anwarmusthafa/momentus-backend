# Generated by Django 5.0.6 on 2024-09-10 16:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0012_notification'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='is_read',
        ),
    ]
