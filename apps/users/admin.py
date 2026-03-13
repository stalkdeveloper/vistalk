# apps/users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'user_type', 'is_active', 'is_staff', 'date_joined']
    list_filter = ['user_type', 'is_active', 'is_staff']
    search_fields = ['email', 'username']
    ordering = ['-date_joined']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('User Type & Role', {
            'fields': ('user_type',)
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('User Type', {
            'fields': ('email', 'user_type',)
        }),
    )