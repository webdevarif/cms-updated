"""
Custom fields for Digital Farmers CMS.

Secure encrypted fields implementation that fixes the security issues
from the previous version.
"""

import base64
import logging
import os
from datetime import timedelta

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.core.exceptions import FieldError
from django.db import models

logger = logging.getLogger(__name__)


def get_encryption_key():
    """
    Get the encryption key from settings.

    Returns:
        str: Base64 encoded encryption key
    """
    key = getattr(settings, "ENCRYPTION_KEY", None)
    if not key:
        raise ValueError(
            "ENCRYPTION_KEY is not set in settings. "
            "Please set ENCRYPTION_KEY in your environment variables or settings file."
        )
    return key


class EncryptedCharField(models.CharField):
    """
    A CharField that encrypts data before saving and decrypts after loading.

    This implementation fixes the security issues from the previous version:
    - Uses a stable encryption key from settings
    - Proper error handling without silent failures
    - Full Django field method implementation
    - Supports migrations properly
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cipher = None

    @property
    def cipher(self):
        """Lazy initialization of cipher to avoid issues during migrations."""
        if self._cipher is None:
            try:
                key = get_encryption_key()
                self._cipher = Fernet(key.encode())
            except Exception as e:
                logger.error(f"Failed to initialize encryption cipher: {e}")
                raise FieldError(f"Encryption field initialization failed: {e}")
        return self._cipher

    def from_db_value(self, value, expression, connection):
        """Decrypt value when loading from database."""
        if value is None:
            return value

        try:
            if isinstance(value, str):
                decrypted = self.cipher.decrypt(value.encode())
                return decrypted.decode("utf-8")
            return value
        except InvalidToken:
            logger.error(f"Failed to decrypt field value - invalid token")
            raise FieldError("Failed to decrypt field value - the data may be corrupted")
        except Exception as e:
            logger.error(f"Error decrypting field value: {e}")
            raise FieldError(f"Failed to decrypt field value: {e}")

    def get_prep_value(self, value):
        """Encrypt value before saving to database."""
        if value is None:
            return value

        try:
            if isinstance(value, str):
                encrypted = self.cipher.encrypt(value.encode("utf-8"))
                return encrypted.decode("utf-8")
            return value
        except Exception as e:
            logger.error(f"Error encrypting field value: {e}")
            raise FieldError(f"Failed to encrypt field value: {e}")

    def to_python(self, value):
        """Convert value to Python data type."""
        if value is None:
            return value
        return str(value)

    def deconstruct(self):
        """Return field information for migrations."""
        name, path, args, kwargs = super().deconstruct()
        # Remove our internal attributes from kwargs
        kwargs.pop("_cipher", None)
        return name, path, args, kwargs


class EncryptedTextField(models.TextField):
    """
    A TextField that encrypts data before saving and decrypts after loading.

    This implementation fixes the security issues from the previous version:
    - Uses a stable encryption key from settings
    - Proper error handling without silent failures
    - Full Django field method implementation
    - Supports migrations properly
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cipher = None

    @property
    def cipher(self):
        """Lazy initialization of cipher to avoid issues during migrations."""
        if self._cipher is None:
            try:
                key = get_encryption_key()
                self._cipher = Fernet(key.encode())
            except Exception as e:
                logger.error(f"Failed to initialize encryption cipher: {e}")
                raise FieldError(f"Encryption field initialization failed: {e}")
        return self._cipher

    def from_db_value(self, value, expression, connection):
        """Decrypt value when loading from database."""
        if value is None:
            return value

        try:
            if isinstance(value, str):
                decrypted = self.cipher.decrypt(value.encode())
                return decrypted.decode("utf-8")
            return value
        except InvalidToken:
            logger.error(f"Failed to decrypt field value - invalid token")
            raise FieldError("Failed to decrypt field value - the data may be corrupted")
        except Exception as e:
            logger.error(f"Error decrypting field value: {e}")
            raise FieldError(f"Failed to decrypt field value: {e}")

    def get_prep_value(self, value):
        """Encrypt value before saving to database."""
        if value is None:
            return value

        try:
            if isinstance(value, str):
                encrypted = self.cipher.encrypt(value.encode("utf-8"))
                return encrypted.decode("utf-8")
            return value
        except Exception as e:
            logger.error(f"Error encrypting field value: {e}")
            raise FieldError(f"Failed to encrypt field value: {e}")

    def to_python(self, value):
        """Convert value to Python data type."""
        if value is None:
            return value
        return str(value)

    def deconstruct(self):
        """Return field information for migrations."""
        name, path, args, kwargs = super().deconstruct()
        # Remove our internal attributes from kwargs
        kwargs.pop("_cipher", None)
        return name, path, args, kwargs
