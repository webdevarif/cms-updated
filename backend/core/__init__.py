"""
Core module for Digital Farmers CMS v2

This module provides the foundational configuration, middleware, and utilities
for the entire application with simplified multi-tenant architecture.
"""

__version__ = "2.0.0"

from core.exceptions import (
    TenantError,
    TenantInactiveError,
    TenantNotFoundError,
    TenantPermissionError,
    TenantValidationError,
)

# Import core components to make them easily accessible
from core.middleware import SecurityMiddleware, TenantMiddleware

__all__ = [
    "TenantMiddleware",
    "SecurityMiddleware",
    "TenantError",
    "TenantNotFoundError",
    "TenantInactiveError",
    "TenantPermissionError",
    "TenantValidationError",
]
