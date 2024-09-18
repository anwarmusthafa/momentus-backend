from django.contrib import admin
from .models import CustomUser , Friendship

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Friendship)
