from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("user", "bio", "image")
