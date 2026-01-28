"""
Custom exceptions for media app.
"""


class MediaUploadError(Exception):
    """Base exception for media upload errors"""

    pass


class InvalidFileTypeError(MediaUploadError):
    """Exception for invalid file types"""

    pass


class FileTooLargeError(MediaUploadError):
    """Exception for files that exceed size limits"""

    pass


class StorageError(MediaUploadError):
    """Exception for storage-related errors"""

    pass
