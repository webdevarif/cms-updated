"""
Core module for Digital Farmers CMS v2

This module provides the foundational configuration, middleware, and utilities
for the entire application with simplified multi-tenant architecture.
"""

__version__ = '2.0.0'

# Import core components to make them easily accessible
from core.middleware import TenantMiddleware, SecurityMiddleware
from core.exceptions import (
    TenantError,
    TenantNotFoundError,
    TenantInactiveError,
    TenantPermissionError,
    TenantValidationError,
)

__all__ = [
    'TenantMiddleware',
    'SecurityMiddleware',
    'TenantError',
    'TenantNotFoundError',
    'TenantInactiveError',
    'TenantPermissionError',
    'TenantValidationError',
]
