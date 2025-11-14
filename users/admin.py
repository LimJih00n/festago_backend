from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'user_type', 'is_staff']
    list_filter = ['user_type', 'is_staff', 'is_active']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('추가 정보', {'fields': ('user_type', 'phone', 'profile_image')}),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('추가 정보', {'fields': ('user_type', 'phone', 'profile_image')}),
    )
