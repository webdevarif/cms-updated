# Mediafile Rules v1.0

## 🎯 Purpose
This document defines strict development rules for the **mediafile** app in CMS-Updated backend, implementing a comprehensive media management system using Cloudflare R2 for storage and ImageKit.io for image processing.

---

## 🏗️ Structure
### **Fixed Directory Structure**
```
mediafile/
├── __init__.py
├── apps.py
├── models/
│   ├── __init__.py
│   ├── media_file.py
│   └── media_folder.py
├── services/
│   ├── __init__.py
│   ├── media_service.py
│   └── imagekit_service.py
├── tasks.py
├── admin.py
├── signals.py
├── exceptions.py
└── v2/
    ├── __init__.py
    ├── urls.py
    ├── serializers/
    │   ├── __init__.py
    │   ├── media_file.py
    │   └── media_folder.py
    └── views/
        ├── __init__.py
        ├── media_views.py
        └── folder_views.py
```

---

## 🔧 Implementation
### **MediaFile Model**
```python
# mediafile/models/media_file.py
import os
from django.db import models
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator
from django.conf import settings
from core.models import TenantModel

class MediaFile(TenantModel):
    """
    Represents a media file stored in Cloudflare R2 with ImageKit.io processing.
    """
    # File types and size limits (in bytes)
    IMAGE_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    VIDEO_MAX_SIZE = 100 * 1024 * 1024  # 100MB
    DOCUMENT_MAX_SIZE = 20 * 1024 * 1024  # 20MB
    
    RESOURCE_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('document', 'Document'),
        ('other', 'Other')
    ]
    
    # Core fields
    original_filename = models.CharField(max_length=255)
    file_extension = models.CharField(max_length=10)
    file_size = models.PositiveIntegerField()
    mime_type = models.CharField(max_length=100)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    
    # R2 storage path (format: store_{id}/media/{folder_path}/filename.xxx)
    storage_path = models.CharField(max_length=512)
    
    # ImageKit.io specific
    imagekit_id = models.CharField(max_length=255, blank=True, null=True)
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    
    # Metadata
    alt_text = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Relations
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE, related_name='media_files')
    folder = models.ForeignKey(
        'mediafile.MediaFolder', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='media_files'
    )
    uploaded_by = models.ForeignKey(
        'accounts.UserAccount', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='uploaded_files'
    )
    
    # Reverse relationships for user media
    user_avatars = models.ManyToManyField(
        'accounts.UserAccount',
        related_name='avatar_media',
        blank=True,
        help_text="Users who use this file as their avatar"
    )
    user_cover_photos = models.ManyToManyField(
        'accounts.UserAccount',
        related_name='cover_photo_media',
        blank=True,
        help_text="Users who use this file as their cover photo"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta(TenantModel.Meta):
        db_table = 'mediafiles_media_file'
        indexes = [
            models.Index(fields=['store', 'resource_type']),
            models.Index(fields=['store', 'folder']),
            models.Index(fields=['created_at']),
            models.Index(fields=['file_size']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return self.original_filename
    
    @property
    def file_size_formatted(self):
        """Return human-readable file size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.file_size < 1024.0:
                return f"{self.file_size:.1f} {unit}"
            self.file_size /= 1024.0
        return f"{self.file_size:.1f} GB"
    
    @property
    def is_image(self):
        return self.resource_type == 'image'
    
    @property
    def is_video(self):
        return self.resource_type == 'video'
    
    @property
    def is_document(self):
        return self.resource_type == 'document'

    def get_absolute_url(self, transformation=None):
        """
        Get the public URL for this media file with optional transformations
        
        Args:
            transformation (str, optional): ImageKit transformation string
            
        Returns:
            str: Public URL with transformations applied
        """
        from .services.media_service import MediaService
        return MediaService().get_media_url(self, transformation)

    def get_thumbnail_url(self, width=200, height=200, crop='fill'):
        """
        Get a thumbnail URL for this media file
        
        Args:
            width (int): Width in pixels
            height (int): Height in pixels
            crop (str): Crop mode (fill, fit, etc.)
            
        Returns:
            str: Thumbnail URL or None if not applicable
        """
        if not self.is_image and not self.is_video:
            return None
            
        transformation = f'tr:w-{width},h-{height},c-{crop}'
        return self.get_absolute_url(transformation)

    def get_presigned_url(self, expires_in=3600):
        """
        Generate a presigned URL for private file access
        
        Args:
            expires_in (int): Expiration time in seconds
            
        Returns:
            str: Presigned URL or None if not applicable
        """
        from .services.media_service import MediaService
        return MediaService().get_presigned_url(self, expires_in)
```

### **MediaFolder Model**
```python
# mediafile/models/media_folder.py
from django.db import models
from django.utils.text import slugify
from core.models import TenantModel

class MediaFolder(TenantModel):
    """
    Represents a folder for organizing media files within a store.
    Supports nested folder structure.
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True)
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE, related_name='media_folders')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    created_by = models.ForeignKey('accounts.UserAccount', on_delete=models.SET_NULL, null=True, related_name='created_folders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(TenantModel.Meta):
        db_table = 'mediafiles_media_folder'
        unique_together = ('store', 'parent', 'slug')
        ordering = ['name']
        indexes = [
            models.Index(fields=['store']),
            models.Index(fields=['parent']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def path(self):
        """Get full folder path as string"""
        if self.parent:
            return f"{self.parent.path}/{self.slug}"
        return self.slug
```

---

## 🔒 Permissions
### **Access Control**
- **Store Owners**: Full CRUD on all media files and folders
- **Staff**: Read-only access to media files, can upload to designated folders
- **Customers**: Can only view their own media files
- **Public**: Limited access to public media files only

### **Validation Rules**
- File type validation based on MIME type
- File size limits per resource type
- Secure filename generation
- Folder nesting depth limits

---

## 🧪 Testing
### **Unit Tests**
```python
# mediafile/tests/test_models.py
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from ..models import MediaFile, MediaFolder

class MediaFileTests(TestCase):
    def setUp(self):
        self.store = Store.objects.create(name='Test Store', slug='test-store')
        self.user = UserAccount.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.folder = MediaFolder.objects.create(
            name='Test Folder',
            store=self.store,
            created_by=self.user
        )
    
    def test_media_file_creation(self):
        """Test creating a media file"""
        media_file = MediaFile.objects.create(
            store=self.store,
            original_filename='test.jpg',
            file_extension='jpg',
            file_size=1024000,
            mime_type='image/jpeg',
            resource_type='image',
            storage_path='store_1/media/test.jpg',
            uploaded_by=self.user,
            folder=self.folder
        )
        
        self.assertEqual(media_file.original_filename, 'test.jpg')
        self.assertEqual(media_file.resource_type, 'image')
        self.assertTrue(media_file.is_image)
        self.assertEqual(media_file.file_size_formatted, '1.0 MB')
    
    def test_folder_path_property(self):
        """Test folder path generation"""
        subfolder = MediaFolder.objects.create(
            name='Sub Folder',
            store=self.store,
            parent=self.folder,
            created_by=self.user
        )
        
        self.assertEqual(subfolder.path, 'test-folder/sub-folder')
```

---

## ⚙️ Services
### **MediaService**
```python
# mediafile/services/media_service.py
import os
import mimetypes
import logging
from urllib.parse import urljoin
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils import timezone
import boto3
from botocore.exceptions import ClientError
import imagekit
from imagekitio import ImageKit

from ..models.media_file import MediaFile
from ..models.media_folder import MediaFolder
from ..exceptions import (
    MediaUploadError,
    InvalidFileTypeError,
    FileTooLargeError,
    StorageError
)

logger = logging.getLogger(__name__)

class MediaService:
    """
    Service class for handling media file operations with Cloudflare R2 and ImageKit.io
    """
    
    # Allowed MIME types and their corresponding resource types
    ALLOWED_MIME_TYPES = {
        'image': [
            'image/jpeg', 'image/png', 'image/gif', 'image/webp', 
            'image/svg+xml', 'image/tiff', 'image/bmp'
        ],
        'video': [
            'video/mp4', 'video/webm', 'video/ogg', 'video/quicktime',
            'video/x-msvideo', 'video/x-ms-wmv', 'video/x-matroska'
        ],
        'document': [
            'application/pdf', 'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'text/plain', 'text/csv', 'application/rtf',
            'application/zip', 'application/x-rar-compressed',
            'application/x-7z-compressed', 'application/x-tar',
            'application/x-gzip'
        ]
    }
    
    def __init__(self):
        """Initialize R2 and ImageKit clients"""
        # Initialize R2 client
        self.s3_client = boto3.client(
            's3',
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name='auto',
            config=boto3.session.Config(signature_version='s3v4')
        )
        
        # Initialize ImageKit
        self.imagekit = ImageKit(
            private_key=settings.IMAGEKIT_PRIVATE_KEY,
            public_key=settings.IMAGEKIT_PUBLIC_KEY,
            url_endpoint=settings.IMAGEKIT_URL_ENDPOINT
        )
    
    def upload_file(self, file_obj, store, user, folder=None, metadata=None):
        """
        Upload a file to R2 and create a MediaFile record
        
        Args:
            file_obj: File object or InMemoryUploadedFile
            store: Store instance
            user: UserAccount instance
            folder: Optional MediaFolder instance
            metadata: Optional dict of metadata
            
        Returns:
            MediaFile: Created media file instance
            
        Raises:
            InvalidFileTypeError: If file type is not allowed
            FileTooLargeError: If file exceeds size limits
            StorageError: If upload to R2 fails
            MediaUploadError: For other upload errors
        """
        try:
            # Validate file
            if not file_obj or not hasattr(file_obj, 'name'):
                raise MediaUploadError("Invalid file object")
                
            # Get file metadata
            file_name = file_obj.name
            file_size = file_obj.size
            mime_type = getattr(file_obj, 'content_type', 
                              mimetypes.guess_type(file_name)[0] or 'application/octet-stream')
            
            # Determine resource type and validate
            resource_type = self._get_resource_type(mime_type, file_name)
            if not resource_type:
                raise InvalidFileTypeError(
                    f"File type {mime_type} is not allowed. "
                    f"Allowed types: {', '.join(self.ALLOWED_MIME_TYPES.keys())}"
                )
            
            # Validate file size
            max_size = getattr(MediaFile, f"{resource_type.upper()}_MAX_SIZE")
            if file_size > max_size:
                raise FileTooLargeError(
                    f"{resource_type.capitalize()} exceeds maximum size of "
                    f"{max_size / (1024 * 1024):.1f}MB"
                )
            
            # Generate storage path
            file_extension = os.path.splitext(file_name)[1].lower()
            base_filename = os.path.splitext(os.path.basename(file_name))[0]
            safe_filename = f"{slugify(base_filename)}{file_extension}"
            
            # Create folder path
            folder_path = f"store_{store.id}/media"
            if folder:
                folder_path = f"{folder_path}/{folder.path}"
            
            # Upload to R2
            r2_key = f"{folder_path}/{safe_filename}"
            
            try:
                if hasattr(file_obj, 'temporary_file_path'):
                    # File is stored on disk
                    self.s3_client.upload_file(
                        file_obj.temporary_file_path(),
                        settings.AWS_STORAGE_BUCKET_NAME,
                        r2_key,
                        ExtraArgs={
                            'ContentType': mime_type,
                            'ACL': 'public-read' if resource_type in ['image', 'video'] else 'private'
                        }
                    )
                else:
                    # File is in memory
                    self.s3_client.upload_fileobj(
                        file_obj,
                        settings.AWS_STORAGE_BUCKET_NAME,
                        r2_key,
                        ExtraArgs={
                            'ContentType': mime_type,
                            'ACL': 'public-read' if resource_type in ['image', 'video'] else 'private'
                        }
                    )
            except ClientError as e:
                logger.error(f"Failed to upload to R2: {str(e)}")
                raise StorageError("Failed to upload file to storage")
            
            # Get file dimensions if image
            width, height = None, None
            if resource_type == 'image':
                try:
                    from PIL import Image
                    if hasattr(file_obj, 'temporary_file_path'):
                        with Image.open(file_obj.temporary_file_path()) as img:
                            width, height = img.size
                    else:
                        # For in-memory files, we need to seek to start
                        file_obj.seek(0)
                        with Image.open(file_obj) as img:
                            width, height = img.size
                        # Reset file pointer for potential reuse
                        file_obj.seek(0)
                except Exception as e:
                    logger.warning(f"Could not get image dimensions: {str(e)}")
            
            # Create MediaFile record
            media_file = MediaFile.objects.create(
                original_filename=file_name,
                file_extension=file_extension.lstrip('.'),
                file_size=file_size,
                mime_type=mime_type,
                resource_type=resource_type,
                storage_path=r2_key,
                width=width,
                height=height,
                store=store,
                folder=folder,
                uploaded_by=user,
                metadata=metadata or {}
            )
            
            # Register with ImageKit for images and videos
            if resource_type in ['image', 'video']:
                try:
                    # Get public URL from R2
                    public_url = f"{settings.AWS_S3_PUBLIC_URL}/{r2_key}"
                    
                    # Upload to ImageKit
                    result = self.imagekit.upload(
                        file=public_url,
                        file_name=safe_filename,
                        options={
                            'folder': folder_path,
                            'is_private_file': False,
                            'use_unique_file_name': False,
                            'response_fields': ['url', 'fileId']
                        }
                    )
                    
                    # Update MediaFile with ImageKit ID
                    media_file.imagekit_id = result['fileId']
                    media_file.save(update_fields=['imagekit_id'])
                    
                except Exception as e:
                    logger.error(f"Failed to register with ImageKit: {str(e)}")
                    # Don't fail the upload, just log the error
            
            return media_file
            
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            if not isinstance(e, (InvalidFileTypeError, FileTooLargeError, StorageError)):
                raise MediaUploadError(f"Failed to upload file: {str(e)}")
            raise
    
    def _get_resource_type(self, mime_type, file_name):
        """
        Determine resource type from MIME type and file name
        
        Args:
            mime_type: MIME type string
            file_name: Original file name
            
        Returns:
            str: Resource type (image, video, document, other) or None if not allowed
        """
        if not mime_type:
            # Try to determine from file extension as fallback
            ext = os.path.splitext(file_name)[1].lower().lstrip('.')
            mime_type = mimetypes.guess_type(file_name)[0] or 'application/octet-stream'
        
        for resource_type, allowed_mimes in self.ALLOWED_MIME_TYPES.items():
            if mime_type in allowed_mimes:
                return resource_type
        
        return None
```

---

## 🔗 Dependencies
```tree
[Related components with @path references]
```
- stores.md for store management
- accounts.md for user management
- logs.md for audit trails
- core.md for base models and utilities

---

## 📋 Migration
### **From Cloudinary to R2 + ImageKit**
```python
# mediafile/management/commands/migrate_media.py
import os
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
import cloudinary
from cloudinary import uploader, api

from ...models import MediaFile, MediaFolder
from ...services.media_service import MediaService

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Migrate media files from Cloudinary to Cloudflare R2 + ImageKit.io'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--store-id',
            type=str,
            help='Store ID to migrate media for (default: all stores)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Maximum number of files to migrate (default: 100)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without making any changes'
        )
    
    def handle(self, *args, **options):
        store_id = options.get('store_id')
        limit = options.get('limit')
        dry_run = options.get('dry_run')
        
        self.stdout.write(self.style.SUCCESS(
            f'Starting media migration for store {store_id or "all"} (dry run: {dry_run})'
        ))
        
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET
        )
        
        # Get media files to migrate
        queryset = MediaFile.objects.all()
        if store_id:
            queryset = queryset.filter(store_id=store_id)
        
        total_count = queryset.count()
        self.stdout.write(f'Found {total_count} media files to migrate')
        
        if not total_count:
            self.stdout.write(self.style.SUCCESS('No media files to migrate'))
            return
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Dry run - no changes will be made'))
        
        migrated_count = 0
        skipped_count = 0
        error_count = 0
        
        media_service = MediaService()
        
        for media_file in queryset[:limit]:
            try:
                self.stdout.write(f'Processing {media_file.original_filename}... ', ending='')
                
                # Skip if already migrated
                if media_file.storage_path and media_file.storage_path.startswith('store_'):
                    self.stdout.write(self.style.WARNING('Already migrated'))
                    skipped_count += 1
                    continue
                
                # Migration logic here...
                migrated_count += 1
                self.stdout.write(self.style.SUCCESS('Done'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Unexpected error: {str(e)}'))
                error_count += 1
                continue
        
        # Print summary
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS('Migration complete!'))
        self.stdout.write(f'Total processed: {migrated_count + skipped_count + error_count}')
        self.stdout.write(f'Successfully migrated: {migrated_count}')
        self.stdout.write(f'Skipped (already migrated): {skipped_count}')
        self.stdout.write(f'Errors: {error_count}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nThis was a dry run. No changes were made.'))
```

---

## ✅ Benefits
- ✅ **Cloud Storage**: Cloudflare R2 with unlimited egress
- ✅ **Image Processing**: ImageKit.io for transformations and optimization
- ✅ **Multi-tenant**: Store-scoped media organization
- ✅ **Flexible Types**: Support for images, videos, documents
- ✅ **Folder Structure**: Nested folder organization
- ✅ **Security**: Private file access with presigned URLs
- ✅ **Performance**: CDN delivery and caching
- ✅ **Cost Effective**: Competitive pricing for storage and bandwidth

---

**Version**: 1.0  
**Last Updated**: 2026-01-26
**Next Review**: 2026-02-25
- [ ] Test migration with a small subset of files
- [ ] Back up Cloudinary data
- [ ] Run migration script
- [ ] Verify all files were migrated correctly
- [ ] Update any hardcoded Cloudinary URLs in the database
### Deployment
- [ ] Set up monitoring for storage usage
- [ ] Configure backups for R2 bucket
- [ ] Set up alerts for quota limits
- [ ] Document operational procedures

## 🔒 Permissions
- Generate API keys or secrets
   - Bypass authentication/authorization
   - Expose sensitive information
2. **Architectural Changes**
   - Change the database schema without approval
   - Modify core business logic
   - Change storage providers (R2/ImageKit)
3. **Production Operations**
   - Run migrations on production
   - Delete production data
   - Modify production configurations

## 🧪 Testing
- [ ] Back up Cloudinary data
- [ ] Run migration script
- [ ] Verify all files were migrated correctly
- [ ] Update any hardcoded Cloudinary URLs in the database
### Deployment
- [ ] Set up monitoring for storage usage
- [ ] Configure backups for R2 bucket
- [ ] Set up alerts for quota limits
- [ ] Document operational procedures

## ⚙️ Services
return MediaService().get_media_url(self, transformation)

    def get_thumbnail_url(self, width=200, height=200, crop='fill'):
        """
        Get a thumbnail URL for this media file
        
        Args:
            width (int): Width in pixels
            height (int): Height in pixels
            crop (str): Crop mode (fill, fit, etc.)
            
        Returns:
            str: Thumbnail URL or None if not applicable
        """
        if not self.is_image and not self.is_video:
            return None
            
        transformation = f'tr:w-{width},h-{height},c-{crop}'
        return self.get_absolute_url(transformation)

    def get_presigned_url(self, expires_in=3600):
        """
        Generate a presigned URL for private file access
        
        Args:
            expires_in (int): Expiration time in seconds
            
        Returns:
            str: Presigned URL or None if not applicable
        """
        from .services.media_service import MediaService
        return MediaService().get_presigned_url(self, expires_in)
```
### MediaFolder
```python
# media/models/media_folder.py
from django.db import models
from django.utils.text import slugify

class MediaFolder(models.Model):
    """
    Represents a folder for organizing media files within a store.
    Supports nested folder structure.
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True)
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE, related_name='media_folders')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    created_by = models.ForeignKey('accounts.UserAccount', on_delete=models.SET_NULL, null=True, related_name='created_folders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('store', 'parent', 'slug')
        ordering = ['name']
        indexes = [
            models.Index(fields=['store']),
            models.Index(fields=['parent']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def path(self):
        """Get full folder path as string"""
        if self.parent:
            return f"{self.parent.path}/{self.slug}"
        return self.slug
```
## Service Layer
### MediaService
```python
# media/services/media_service.py
import os
import mimetypes
import logging
from urllib.parse import urljoin
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils import timezone
import boto3
from botocore.exceptions import ClientError
import imagekit
from imagekitio import ImageKit

from ..models.media_file import MediaFile
from ..models.media_folder import MediaFolder
from ..exceptions import (
    MediaUploadError,
    InvalidFileTypeError,
    FileTooLargeError,
    StorageError
)

logger = logging.getLogger(__name__)

class MediaService:
    """
    Service class for handling media file operations with Cloudflare R2 and ImageKit.io
    """
    
    # Allowed MIME types and their corresponding resource types
    ALLOWED_MIME_TYPES = {
        'image': [
            'image/jpeg', 'image/png', 'image/gif', 'image/webp', 
            'image/svg+xml', 'image/tiff', 'image/bmp'
        ],
        'video': [
            'video/mp4', 'video/webm', 'video/ogg', 'video/quicktime',
            'video/x-msvideo', 'video/x-ms-wmv', 'video/x-matroska'
        ],
        'document': [
            'application/pdf', 'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'text/plain', 'text/csv', 'application/rtf',
            'application/zip', 'application/x-rar-compressed',
            'application/x-7z-compressed', 'application/x-tar',
            'application/x-gzip'
        ]
    }
    
    def __init__(self):
        """Initialize R2 and ImageKit clients"""
        # Initialize R2 client
        self.s3_client = boto3.client(
            's3',
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name='auto',
            config=boto3.session.Config(signature_version='s3v4')
        )
        
        # Initialize ImageKit
        self.imagekit = ImageKit(
            private_key=settings.IMAGEKIT_PRIVATE_KEY,
            public_key=settings.IMAGEKIT_PUBLIC_KEY,
            url_endpoint=settings.IMAGEKIT_URL_ENDPOINT
        )
    
    def upload_file(self, file_obj, store, user, folder=None, metadata=None):
        """
        Upload a file to R2 and create a MediaFile record
        
        Args:
            file_obj: File object or InMemoryUploadedFile
            store: Store instance
            user: UserAccount instance
            folder: Optional MediaFolder instance
            metadata: Optional dict of metadata
            
        Returns:
            MediaFile: Created media file instance
            
        Raises:
            InvalidFileTypeError: If file type is not allowed
            FileTooLargeError: If file exceeds size limits
            StorageError: If upload to R2 fails
            MediaUploadError: For other upload errors
        """
        try:
            # Validate file
            if not file_obj or not hasattr(file_obj, 'name'):
                raise MediaUploadError("Invalid file object")
                
            # Get file metadata
            file_name = file_obj.name
            file_size = file_obj.size
            mime_type = getattr(file_obj, 'content_type', 
                              mimetypes.guess_type(file_name)[0] or 'application/octet-stream')
            
            # Determine resource type and validate
            resource_type = self._get_resource_type(mime_type, file_name)
            if not resource_type:
                raise InvalidFileTypeError(
                    f"File type {mime_type} is not allowed. "
                    f"Allowed types: {', '.join(self.ALLOWED_MIME_TYPES.keys())}"
                )
            
            # Validate file size
            max_size = getattr(MediaFile, f"{resource_type.upper()}_MAX_SIZE")
            if file_size > max_size:
                raise FileTooLargeError(
                    f"{resource_type.capitalize()} exceeds maximum size of "
                    f"{max_size / (1024 * 1024):.1f}MB"
                )
            
            # Generate storage path
            file_extension = os.path.splitext(file_name)[1].lower()
            base_filename = os.path.splitext(os.path.basename(file_name))[0]
            safe_filename = f"{slugify(base_filename)}{file_extension}"
            
            # Create folder path
            folder_path = f"store_{store.id}/media"
            if folder:
                folder_path = f"{folder_path}/{folder.path}"
            
            # Upload to R2
            r2_key = f"{folder_path}/{safe_filename}"
            
            try:
                if hasattr(file_obj, 'temporary_file_path'):
                    # File is stored on disk
                    self.s3_client.upload_file(
                        file_obj.temporary_file_path(),
                        settings.AWS_STORAGE_BUCKET_NAME,
                        r2_key,
                        ExtraArgs={
                            'ContentType': mime_type,
                            'ACL': 'public-read' if resource_type in ['image', 'video'] else 'private'
                        }
                    )
                else:
                    # File is in memory
                    self.s3_client.upload_fileobj(
                        file_obj,
                        settings.AWS_STORAGE_BUCKET_NAME,
                        r2_key,
                        ExtraArgs={
                            'ContentType': mime_type,
                            'ACL': 'public-read' if resource_type in ['image', 'video'] else 'private'
                        }
                    )
            except ClientError as e:
                logger.error(f"Failed to upload to R2: {str(e)}")
                raise StorageError("Failed to upload file to storage")
            
            # Get file dimensions if image
            width, height = None, None
            if resource_type == 'image':
                try:
                    from PIL import Image
                    if hasattr(file_obj, 'temporary_file_path'):
                        with Image.open(file_obj.temporary_file_path()) as img:
                            width, height = img.size
                    else:
                        # For in-memory files, we need to seek to start
                        file_obj.seek(0)
                        with Image.open(file_obj) as img:
                            width, height = img.size
                        # Reset file pointer for potential reuse
                        file_obj.seek(0)
                except Exception as e:
                    logger.warning(f"Could not get image dimensions: {str(e)}")
            
            # Create MediaFile record
            media_file = MediaFile.objects.create(
                original_filename=file_name,
                file_extension=file_extension.lstrip('.'),
                file_size=file_size,
                mime_type=mime_type,
                resource_type=resource_type,
                storage_path=r2_key,
                width=width,
                height=height,
                store=store,
                folder=folder,
                uploaded_by=user,
                metadata=metadata or {}
            )
            
            # Register with ImageKit for images and videos
            if resource_type in ['image', 'video']:
                try:
                    # Get public URL from R2
                    public_url = f"{settings.AWS_S3_PUBLIC_URL}/{r2_key}"
                    
                    # Upload to ImageKit
                    result = self.imagekit.upload(
                        file=public_url,
                        file_name=safe_filename,
                        options={
                            'folder': folder_path,
                            'is_private_file': False,
                            'use_unique_file_name': False,
                            'response_fields': ['url', 'fileId']
                        }
                    )
                    
                    # Update MediaFile with ImageKit ID
                    media_file.imagekit_id = result['fileId']
                    media_file.save(update_fields=['imagekit_id'])
                    
                except Exception as e:
                    logger.error(f"Failed to register with ImageKit: {str(e)}")
                    # Don't fail the upload, just log the error
            
            # Log the upload
            self._log_media_action(
                action='UPLOAD',
                user=user,
                store=store,
                media_file=media_file,
                metadata={
                    'file_size': file_size,
                    'mime_type': mime_type,
                    'folder': folder.name if folder else None
                }
            )
            
            return media_file
            
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            if not isinstance(e, (InvalidFileTypeError, FileTooLargeError, StorageError)):
                raise MediaUploadError(f"Failed to upload file: {str(e)}")
            raise
    
    def delete_media(self, media_file, user):
        """
        Delete a media file from storage and database
        
        Args:
            media_file: MediaFile instance to delete
            user: UserAccount performing the deletion
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            store = media_file.store
            
            # Delete from R2
            try:
                self.s3_client.delete_object(
                    Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                    Key=media_file.storage_path
                )
            except ClientError as e:
                logger.error(f"Failed to delete from R2: {str(e)}")
                # Continue with DB deletion even if R2 delete fails
            
            # Delete from ImageKit if it exists
            if media_file.imagekit_id:
                try:
                    self.imagekit.delete_file(media_file.imagekit_id)
                except Exception as e:
                    logger.error(f"Failed to delete from ImageKit: {str(e)}")
            
            # Log before deletion (to have the ID)
            self._log_media_action(
                action='DELETE',
                user=user,
                store=store,
                media_file=media_file
            )
            
            # Delete from database
            media_file.delete()
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting media file {media_file.id}: {str(e)}")
            raise MediaUploadError(f"Failed to delete media file: {str(e)}")
    
    def get_media_url(self, media_file, transformation=None):
        """
        Get URL for a media file with optional transformations
        
        Args:
            media_file: MediaFile instance
            transformation: Optional transformation string for ImageKit
            
        Returns:
            str: Public URL to the media file
        """
        if not media_file:
            return None
            
        # For private files, generate a presigned URL
        if media_file.resource_type not in ['image', 'video']:
            return self.get_presigned_url(media_file)
            
        # For public files, use ImageKit if available
        if media_file.imagekit_id:
            try:
                url = f"{settings.IMAGEKIT_URL}/{media_file.storage_path}"
                if transformation:
                    url = f"{url}?tr={transformation}"
                return url
            except Exception as e:
                logger.warning(f"Failed to get ImageKit URL: {str(e)}")
                # Fall back to R2 URL
        
        # Fallback to R2 public URL
        return f"{settings.AWS_S3_PUBLIC_URL}/{media_file.storage_path}"
    
    def get_presigned_url(self, media_file, expires_in=3600):
        """
        Generate a presigned URL for private file access
        
        Args:
            media_file: MediaFile instance
            expires_in: Expiration time in seconds
            
        Returns:
            str: Presigned URL or None if not applicable
        """
        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                    'Key': media_file.storage_path,
                    'ResponseContentType': media_file.mime_type,
                    'ResponseContentDisposition': f'attachment; filename="{media_file.original_filename}"'
                },
                ExpiresIn=expires_in
            )
            return response
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {str(e)}")
            return None
    
    def get_thumbnail_url(self, media_file, width=200, height=200, crop='fill'):
        """
        Get a thumbnail URL for a media file
        
        Args:
            media_file: MediaFile instance
            width: Thumbnail width in pixels
            height: Thumbnail height in pixels
            crop: Crop mode (fill, fit, etc.)
            
        Returns:
            str: Thumbnail URL or None if not applicable
        """
        if not media_file or media_file.resource_type not in ['image', 'video']:
            return None
            
        transformation = f'w-{width},h-{height},c-{crop}'
        return self.get_media_url(media_file, transformation)
    
    def _get_resource_type(self, mime_type, file_name):
        """
        Determine resource type from MIME type and file name
        
        Args:
            mime_type: MIME type string
            file_name: Original file name
            
        Returns:
            str: Resource type (image, video, document, other) or None if not allowed
        """
        if not mime_type:
            # Try to determine from file extension as fallback
            ext = os.path.splitext(file_name)[1].lower().lstrip('.')
            mime_type = mimetypes.guess_type(file_name)[0] or 'application/octet-stream'
        
        for resource_type, allowed_mimes in self.ALLOWED_MIME_TYPES.items():
            if mime_type in allowed_mimes:
                return resource_type
        
        return None
    
    def _log_media_action(self, action, user, store, media_file, metadata=None):
        """
        Log media-related actions to the activity log
        
        Args:
            action: Action type (UPLOAD, DELETE, etc.)
            user: UserAccount performing the action
            store: Store the action belongs to
            media_file: MediaFile being acted upon
            metadata: Additional metadata to include in the log
        """
        from logs.services.log_service import log_event_async
        
        log_data = {
            'event_type': 'MEDIA_' + action,
            'message': f"Media file {action.lower()}: {media_file.original_filename}",
            'user': user,
            'store': store,
            'entity_type': 'MediaFile',
            'entity_id': media_file.id,
            'metadata': {
                'file_size': media_file.file_size,
                'mime_type': media_file.mime_type,
                'resource_type': media_file.resource_type,
                'folder': media_file.folder.name if media_file.folder else None,
                **(metadata or {})
            }
        }
        
        log_event_async.delay(log_data)
```
### ImageKitService (Optional)
```python
# media/services/imagekit_service.py
from imagekitio import ImageKit
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class ImageKitService:
    """
    Service class for advanced ImageKit.io operations
    """
    
    def __init__(self):
        self.client = ImageKit(
            private_key=settings.IMAGEKIT_PRIVATE_KEY,
            public_key=settings.IMAGEKIT_PUBLIC_KEY,
            url_endpoint=settings.IMAGEKIT_URL_ENDPOINT
        )
    
    def get_transformed_url(self, image_url, transformations):
        """
        Get URL for an image with transformations applied
        
        Args:
            image_url: Source image URL
            transformations: List of transformation dicts
                Example: [{"height": 300, "width": 400}]
                
        Returns:
            str: Transformed image URL
        """
        try:
            return self.client.url({
                'path': image_url,
                'transformation': transformations
            })
        except Exception as e:
            logger.error(f"Failed to generate transformed URL: {str(e)}")
            return image_url
    
    def get_video_thumbnail(self, video_url, width=320, height=180):
        """
        Generate a thumbnail for a video
        
        Args:
            video_url: Source video URL
            width: Thumbnail width
            height: Thumbnail height
            
        Returns:
            str: URL to the generated thumbnail
        """
        try:
            return self.client.url({
                'path': video_url,
                'transformation': [
                    {
                        'format': 'jpg',
                        'height': height,
                        'width': width,
                        'crop': 'fill',
                        'quality': '80',
                        'progressive': 'true'
                    }
                ]
            })
        except Exception as e:
            logger.error(f"Failed to generate video thumbnail: {str(e)}")
            return None
    
    def bulk_optimize(self, file_ids, transformations=None):
        """
        Optimize multiple images in bulk
        
        Args:
            file_ids: List of ImageKit file IDs
            transformations: Optional transformations to apply
            
        Returns:
            dict: Result of the bulk operation
        """
        try:
            return self.client.bulk_file_operations(
                file_ids=file_ids,
                transformations=transformations or []
            )
        except Exception as e:
            logger.error(f"Bulk optimize failed: {str(e)}")
            return {'success': False, 'error': str(e)}
```

## 🔗 Dependencies
[Dependencies content to be added]

## 📋 Migration
### migrate_media.py
```python
# media/management/commands/migrate_media.py
import os
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
import cloudinary
from cloudinary import uploader, api

from ...models import MediaFile, MediaFolder
from ...services.media_service import MediaService

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Migrate media files from Cloudinary to Cloudflare R2 + ImageKit.io'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--store-id',
            type=str,
            help='Store ID to migrate media for (default: all stores)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Maximum number of files to migrate (default: 100)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without making any changes'
        )
    
    def handle(self, *args, **options):
        store_id = options.get('store_id')
        limit = options.get('limit')
        dry_run = options.get('dry_run')
        
        self.stdout.write(self.style.SUCCESS(
            f'Starting media migration for store {store_id or "all"} (dry run: {dry_run})'
        ))
        
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET
        )
        
        # Get media files to migrate
        queryset = MediaFile.objects.all()
        if store_id:
            queryset = queryset.filter(store_id=store_id)
        
        total_count = queryset.count()
        self.stdout.write(f'Found {total_count} media files to migrate')
        
        if not total_count:
            self.stdout.write(self.style.SUCCESS('No media files to migrate'))
            return
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Dry run - no changes will be made'))
        
        migrated_count = 0
        skipped_count = 0
        error_count = 0
        
        media_service = MediaService()
        
        for media_file in queryset[:limit]:
            try:
                self.stdout.write(f'Processing {media_file.original_filename}... ', ending='')
                
                # Skip if already migrated
                if media_file.storage_path and media_file.storage_path.startswith('store_'):
                    self.stdout.write(self.style.WARNING('Already migrated'))
                    skipped_count += 1
                    continue
                
                # Download from Cloudinary
                try:
                    cloudinary_url = f"v{media_file.version}/{media_file.public_id}.{media_file.format}"
                    temp_file = f'/tmp/{media_file.public_id}.{media_file.format}'
                    
                    if not dry_run:
                        # Download the file
                        with open(temp_file, 'wb') as f:
                            result = cloudinary.utils.cloudinary_url(cloudinary_url)[0]
                            f.write(requests.get(result).content)
                        
                        # Upload to R2 + ImageKit
                        with open(temp_file, 'rb') as f:
                            uploaded_file = SimpleUploadedFile(
                                name=media_file.original_filename,
                                content=f.read(),
                                content_type=media_file.mime_type
                            )
                            
                            # Get folder if exists
                            folder = None
                            if media_file.folder_id:
                                try:
                                    folder = MediaFolder.objects.get(id=media_file.folder_id)
                                except MediaFolder.DoesNotExist:
                                    pass
                            
                            # Upload the file
                            media_service.upload_file(
                                file_obj=uploaded_file,
                                store=media_file.store,
                                user=media_file.uploaded_by,
                                folder=folder,
                                metadata={
                                    'migrated_from_cloudinary': True,
                                    'cloudinary_public_id': media_file.public_id
                                }
                            )
                        
                        # Delete local temp file
                        os.remove(temp_file)
                        
                        # Delete from Cloudinary if migration is successful
                        if not dry_run and settings.CLOUDINARY_DELETE_AFTER_MIGRATE:
                            try:
                                uploader.destroy(media_file.public_id)
                            except Exception as e:
                                logger.error(f"Failed to delete from Cloudinary: {str(e)}")
                
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
                    error_count += 1
                    continue
                
                migrated_count += 1
                self.stdout.write(self.style.SUCCESS('Done'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Unexpected error: {str(e)}'))
                error_count += 1
                continue
        
        # Print summary
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS('Migration complete!'))
        self.stdout.write(f'Total processed: {migrated_count + skipped_count + error_count}')
        self.stdout.write(f'Successfully migrated: {migrated_count}')
        self.stdout.write(f'Skipped (already migrated): {skipped_count}')
        self.stdout.write(f'Errors: {error_count}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nThis was a dry run. No changes were made.'))
```

## ✅ Benefits
### Processing
- Use Celery for async post-upload processing:
  - Thumbnail generation
  - Metadata extraction
  - Virus scanning
  - File optimization
- Process large uploads in chunks (resumable uploads)
- Implement background processing for batch operations
### Caching
- Cache ImageKit URLs aggressively: `Cache-Control: max-age=31536000` for public assets
- Implement CDN caching for frequently accessed media
- Use stale-while-revalidate for dynamic transformations
- Cache folder hierarchies to reduce database load
### Optimization
- Enable gzip/brotli compression for text-based assets
- Use WebP/AVIF formats for web images when supported
- Implement lazy loading for below-the-fold media
- Optimize video delivery with adaptive bitrate streaming

---
**Version**: 1.0  
**Last Updated**: 2026-01-26
**Next Review**: 2026-02-25
