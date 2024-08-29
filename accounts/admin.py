from django.contrib import admin
from .models import CustomUser , Friends

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Friends)
