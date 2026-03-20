from django.db import models
from django.conf import settings


class Upload(models.Model):

    DISK_CHOICES = [
        ('public',  'Public'),
        ('private', 'Private'),
    ]

    DRIVER_CHOICES = [
        ('local', 'Local'),
        ('s3',    'Amazon S3'),
        ('r2',    'Cloudflare R2'),
        ('gcs',   'Google Cloud'),
    ]
    # ─── Polymorphic relation ──────────────────────────────────
    uploadable_type = models.CharField(max_length=100)  # 'User', 'Task', 'Comment'
    uploadable_id   = models.PositiveBigIntegerField()

    # ─── File identity ─────────────────────────────────────────
    file_name     = models.CharField(max_length=255)   # uuid stored name
    original_name = models.CharField(max_length=255)   # original from user
    extension     = models.CharField(max_length=50)    # 'pdf', 'png', 'mp4'
    mime_type     = models.CharField(max_length=100)   # 'image/jpeg'

    # ─── mime_category: broad technical type ──────────────────
    # Auto-set by service — never by user
    # Values: 'image' | 'video' | 'audio' | 'document' | 'other'
    mime_category = models.CharField(max_length=20, null=True, blank=True)

    # ─── file_type: purpose/context — free string ─────────────
    # User    → 'avatar' | 'cover'
    # Task    → 'attachment' | 'cover'
    # Comment → 'attachment'
    # Board   → 'background'
    # Org     → 'logo' | 'cover'
    file_type = models.CharField(max_length=100, null=True, blank=True)

    disk      = models.CharField(max_length=20, choices=DISK_CHOICES, default='public')
    driver    = models.CharField(max_length=20, choices=DRIVER_CHOICES, default='local')
    path      = models.CharField(max_length=500)    # relative path
    url       = models.CharField(max_length=1000)   # full URL

    size = models.PositiveBigIntegerField(help_text="Size in bytes")

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploads',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['uploadable_type', 'uploadable_id']),
            models.Index(fields=['uploadable_type', 'file_type']),
            models.Index(fields=['-created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.uploadable_type}#{self.uploadable_id} — {self.file_type or 'file'} — {self.original_name}"

    @property
    def human_size(self):
        size = self.size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}" if unit != 'B' else f"{size} B"
            size /= 1024
        return f"{size:.1f} TB"