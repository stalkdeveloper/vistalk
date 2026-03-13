# apps/roles/models.py
from django.db import models
from django.conf import settings


class Permission(models.Model):
    """Individual permissions like 'can_create_post', 'can_delete_user'"""
    name = models.CharField(max_length=100, unique=True)        # e.g. 'can_create_post'
    display_name = models.CharField(max_length=100)             # e.g. 'Can Create Post'
    group = models.CharField(max_length=50, blank=True)         # e.g. 'posts', 'users'
    description = models.TextField(blank=True)

    def __str__(self):
        return self.display_name

    class Meta:
        db_table = 'permissions'
        ordering = ['group', 'name']


class Role(models.Model):
    """Roles like 'admin', 'user', 'moderator'"""
    name = models.CharField(max_length=50, unique=True)         # e.g. 'admin'
    display_name = models.CharField(max_length=100)             # e.g. 'Administrator'
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(Permission, blank=True, related_name='roles')
    is_default = models.BooleanField(default=False)             # Default role for new users
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.display_name

    def has_permission(self, permission_name):
        return self.permissions.filter(name=permission_name).exists()

    class Meta:
        db_table = 'roles'


class UserRole(models.Model):
    """Assign roles to users (many-to-many with extra fields)"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_roles'
    )
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_roles')
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_roles'
        unique_together = ('user', 'role')

    def __str__(self):
        return f"{self.user.email} → {self.role.name}"