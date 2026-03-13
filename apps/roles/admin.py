# apps/roles/admin.py
from django.contrib import admin
from .models import Role, Permission, UserRole


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name', 'group']
    list_filter = ['group']
    search_fields = ['name', 'display_name']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name', 'is_default']
    filter_horizontal = ['permissions']
    list_filter = ['is_default']


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'assigned_at']
    list_filter = ['role']
    search_fields = ['user__email', 'role__name']