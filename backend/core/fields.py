"""
Custom fields for Digital Farmers CMS.
"""

import base64
import os

from cryptography.fernet import Fernet
from django.conf import settings
from django.db import models


class EncryptedCharField(models.CharField):
    """
    A CharField that encrypts data before saving and decrypts after loading.
    """

    def __init__(self, *args, **kwargs):
        if not hasattr(settings, "ENCRYPTION_KEY"):
            # Generate a key if not set in settings
            settings.ENCRYPTION_KEY = base64.urlsafe_b64encode(os.urandom(32)).decode()

        self.cipher = Fernet(settings.ENCRYPTION_KEY.encode())
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        try:
            return self.cipher.decrypt(value.encode()).decode()
        except Exception:
            # Return the value as-is if decryption fails
            return value

    def get_prep_value(self, value):
        if value is None:
            return value
        try:
            return self.cipher.encrypt(value.encode()).decode()
        except Exception:
            # Return the value as-is if encryption fails
            return value


class EncryptedTextField(models.TextField):
    """
    A TextField that encrypts data before saving and decrypts after loading.
    """

    def __init__(self, *args, **kwargs):
        if not hasattr(settings, "ENCRYPTION_KEY"):
            # Generate a key if not set in settings
            settings.ENCRYPTION_KEY = base64.urlsafe_b64encode(os.urandom(32)).decode()

        self.cipher = Fernet(settings.ENCRYPTION_KEY.encode())
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        try:
            return self.cipher.decrypt(value.encode()).decode()
        except Exception:
            # Return the value as-is if decryption fails
            return value

    def get_prep_value(self, value):
        if value is None:
            return value
        try:
            return self.cipher.encrypt(value.encode()).decode()
        except Exception:
            # Return the value as-is if encryption fails
            return value
