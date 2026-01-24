"""
Custom exceptions for Digital Farmers CMS.
"""
from django.core.exceptions import ValidationError


class TenantError(Exception):
    """Base tenant exception"""
    pass


class TenantNotFoundError(TenantError):
    """Raised when tenant is not found"""
    pass


class TenantInactiveError(TenantError):
    """Raised when tenant is inactive"""
    pass


class TenantPermissionError(TenantError):
    """Raised when tenant doesn't have permission"""
    pass


class TenantValidationError(ValidationError):
    """Raised when tenant validation fails"""
    pass


class StoreError(Exception):
    """Base store exception"""
    pass


class StoreNotFoundError(StoreError):
    """Raised when store is not found"""
    pass


class StoreInactiveError(StoreError):
    """Raised when store is inactive"""
    pass


class StorePermissionError(StoreError):
    """Raised when store doesn't have permission"""
    pass


class StoreValidationError(ValidationError):
    """Raised when store validation fails"""
    pass


class ConfigurationError(Exception):
    """Raised when configuration is invalid"""
    pass


class ServiceUnavailableError(Exception):
    """Raised when a service is unavailable"""
    pass


class ValidationError(Exception):
    """Raised when validation fails"""
    pass
