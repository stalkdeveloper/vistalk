# apps/users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('system', 'System'),      # Company employees/staff - only login, no register
        ('platform', 'Platform'),  # Web users - can register
    ]

    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='platform'
    )

    email = models.EmailField(unique=True)

    # We'll use email as the primary login field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def is_system_user(self):
        return self.user_type == 'system'

    def is_platform_user(self):
        return self.user_type == 'platform'

    def __str__(self):
        return f"{self.email} ({self.user_type})"

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'