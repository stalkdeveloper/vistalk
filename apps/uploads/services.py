import uuid, mimetypes
from pathlib import Path
from django.conf import settings
from django.core.files.storage import default_storage
from .models import Upload

MIME_CATEGORY_MAP = {
    'image':    ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml'],
    'video':    ['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/webm'],
    'audio':    ['audio/mpeg', 'audio/wav', 'audio/ogg'],
    'document': [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain', 'text/csv',
    ],
}

def _get_mime_category(mime: str) -> str:
    for category, mimes in MIME_CATEGORY_MAP.items():
        if mime in mimes:
            return category
    return 'other'

def _get_driver() -> str:
    if getattr(settings, 'AWS_ACCESS_KEY_ID', None) and \
       getattr(settings, 'AWS_STORAGE_BUCKET', None):
        return 's3'
    return 'local'

def _build_url(saved_path: str) -> str:
    if _get_driver() == 's3':
        domain = getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', None)
        if domain:
            return f"https://{domain}/{saved_path}"
        bucket = settings.AWS_STORAGE_BUCKET
        region = getattr(settings, 'AWS_S3_REGION', 'ap-south-1')
        return f"https://{bucket}.s3.{region}.amazonaws.com/{saved_path}"
    return f"{settings.MEDIA_URL}{saved_path}"


def store_upload(
    file,
    uploadable_type: str,   # 'User', 'Task', 'Comment'
    uploadable_id:   int,
    user,
    file_type: str = None,  # 'avatar', 'attachment', 'cover', 'logo'
    disk:      str = 'public',
) -> Upload:

    ext         = Path(file.name).suffix.lower().lstrip('.')
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    folder      = f"uploads/{uploadable_type.lower()}s"  # uploads/users/ uploads/tasks/
    rel_path    = f"{folder}/{unique_name}"

    saved_path  = default_storage.save(rel_path, file)
    mime        = file.content_type or mimetypes.guess_type(file.name)[0] or 'application/octet-stream'

    return Upload.objects.create(
        uploadable_type = uploadable_type,
        uploadable_id   = uploadable_id,
        uploaded_by     = user,
        file_name       = unique_name,
        original_name   = file.name,
        extension       = ext,
        mime_type       = mime,
        mime_category   = _get_mime_category(mime),
        file_type       = file_type,
        disk            = disk,
        driver          = _get_driver(),
        path            = saved_path,
        url             = _build_url(saved_path),
        size            = file.size,
    )


def get_uploads(obj, file_type: str = None):
    qs = Upload.objects.filter(
        uploadable_type = obj.__class__.__name__,
        uploadable_id   = obj.pk,
    )
    if file_type:
        qs = qs.filter(file_type=file_type)
    return qs


def get_first(obj, file_type: str = None) -> Upload | None:
    return get_uploads(obj, file_type).first()


def delete_upload(upload: Upload) -> None:
    try:
        if default_storage.exists(upload.path):
            default_storage.delete(upload.path)
    except Exception:
        pass
    upload.delete()