# Generated by Django 5.0.6 on 2024-07-30 05:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0005_like'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='is_blocked',
            field=models.BooleanField(default=False),
        ),
    ]