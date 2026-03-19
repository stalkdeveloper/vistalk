# apps/users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('system',   'System'),    # Staff / employees - login only
        ('platform', 'Platform'),  # Web users - can register
    ]

    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='platform',
    )

    # Django's AbstractUser already has first_name and last_name;
    # we add middle_name and keep email as the login field.
    middle_name = models.CharField(max_length=150, blank=True)

    email = models.EmailField(unique=True)

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username']

    # ── helpers ───────────────────────────────
    def get_full_name(self):
        parts = [self.first_name, self.middle_name, self.last_name]
        return ' '.join(p for p in parts if p).strip() or self.username

    def is_system_user(self):
        return self.user_type == 'system'

    def is_platform_user(self):
        return self.user_type == 'platform'

    def __str__(self):
        return f"{self.email} ({self.user_type})"

    class Meta:
        db_table       = 'users'
        verbose_name   = 'User'
        verbose_name_plural = 'Users'