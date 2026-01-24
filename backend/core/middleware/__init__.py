"""
Middleware package for Digital Farmers CMS.

This package contains custom middleware components.
"""

# Import middleware classes to make them available when importing from core.middleware
from .tenant import TenantMiddleware  # noqa
from .security import SecurityMiddleware  # noqa
