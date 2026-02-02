"""
Pages models - using posts models for page content.
"""

# Pages app uses the posts models for page content
# Import from posts app to maintain consistency
from apps.posts.models import Post, PostRevision, PostType, Taxonomy, Term

# Import navigation models
from .navigation import Menu, MenuItem

# Removed erroneous import as Page is not defined in pages.py

# Page-specific constants
PAGE_TYPE_SLUG = "page"

__all__ = [
    "Post",
    "PostType",
    "Taxonomy",
    "Term",
    "PostRevision",
    "PAGE_TYPE_SLUG",
    "Menu",
    "MenuItem",
]
