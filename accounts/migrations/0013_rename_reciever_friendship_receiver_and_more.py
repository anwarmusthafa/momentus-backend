# Generated by Django 5.0.6 on 2024-09-21 18:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_rename_user_two_friendship_reciever_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='friendship',
            old_name='reciever',
            new_name='receiver',
        ),
        migrations.AlterUniqueTogether(
            name='friendship',
            unique_together={('sender', 'receiver')},
        ),
    ]
