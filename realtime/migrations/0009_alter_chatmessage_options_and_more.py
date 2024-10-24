# Generated by Django 5.0.6 on 2024-08-21 19:06

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0008_alter_chatmessage_room'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='chatmessage',
            options={'ordering': ['timestamp']},
        ),
        migrations.RenameField(
            model_name='chatmessage',
            old_name='message',
            new_name='content',
        ),
        migrations.RemoveField(
            model_name='chatmessage',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='chatmessage',
            name='receiver',
        ),
        migrations.RemoveField(
            model_name='chatmessage',
            name='room',
        ),
        migrations.RemoveField(
            model_name='chatmessage',
            name='status',
        ),
        migrations.RemoveField(
            model_name='chatmessage',
            name='updated_at',
        ),
        migrations.RemoveField(
            model_name='chatroom',
            name='updated_at',
        ),
        migrations.AddField(
            model_name='chatmessage',
            name='chat_room',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='realtime.chatroom'),
        ),
        migrations.AddField(
            model_name='chatmessage',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='chat_images/'),
        ),
        migrations.AddField(
            model_name='chatmessage',
            name='seen_by',
            field=models.ManyToManyField(blank=True, related_name='seen_messages', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='chatmessage',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='chatroom',
            name='is_group',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='chatmessage',
            name='sender',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='chatroom',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.CreateModel(
            name='ChatParticipant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('chat_room', models.ForeignKey(blank=True, default=0, null=True, on_delete=django.db.models.deletion.CASCADE, to='realtime.chatroom')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='chatroom',
            name='participants',
            field=models.ManyToManyField(related_name='chat_rooms', through='realtime.ChatParticipant', to=settings.AUTH_USER_MODEL),
        ),
    ]
