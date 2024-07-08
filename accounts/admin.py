# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'full_name', 'momentus_user_name', 'is_prime', 'email_verified')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('full_name', 'momentus_user_name', 'bio', 'email', 'email_verified', 'verification_code')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'full_name', 'momentus_user_name', 'password1', 'password2', 'email', 'is_prime', 'bio', 'email_verified', 'verification_code'),
        }),
    )
    search_fields = ('username', 'full_name', 'momentus_user_name', 'email')
    list_filter = ('is_prime', 'email_verified')
    ordering = ('username',)

admin.site.register(CustomUser, CustomUserAdmin)
