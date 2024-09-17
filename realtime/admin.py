from django.contrib import admin
from .models import ChatMessage , ChatRoom, ChatParticipant , Notification

# Register your models here.
class ChatRoomParticipantInline(admin.TabularInline):
    model = ChatParticipant
    extra = 1  # Number of empty forms to display initially

class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_group', 'created_at')  # Display 'created_at' in the list view
    fields = ('name', 'is_group')  # Exclude 'participants' from the form
    inlines = [ChatRoomParticipantInline]  # Add inline model admin for managing participants
    search_fields = ('name',)
    list_filter = ('is_group',)

admin.site.register(ChatMessage)
admin.site.register(ChatRoom, ChatRoomAdmin)
admin.site.register(ChatParticipant)
admin.site.register(Notification)
