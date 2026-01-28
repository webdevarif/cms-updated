"""
Pages models - using posts models for page content.
"""
# Pages app uses the posts models for page content
# Import from posts app to maintain consistency
from apps.posts.models import Post, PostRevision, PostType, Taxonomy, Term
from apps.posts.models.posts_search_vectors import PostSearchVectorMixin

# Page-specific constants
PAGE_TYPE_SLUG = "page"

__all__ = [
    "Post",
    "PostType",
    "Taxonomy",
    "Term",
    "PostRevision",
    "PostSearchVectorMixin",
    "PAGE_TYPE_SLUG",
]
