"""
Settings package for Digital Farmers CMS.

This package contains all the configuration settings for different environments.
"""

from .base import *  # noqa
# from .giftcards import *  # Temporarily commented out for migration

# Import the appropriate settings based on the environment
# This will be overridden by the specific environment settings
# (development.py, production.py, testing.py)
