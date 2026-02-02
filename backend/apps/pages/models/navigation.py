"""
Navigation models for pages app.
"""

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify


class Menu(models.Model):
    """
    Navigation menu for a store.

    Represents a collection of menu items that can be displayed
    in the frontend navigation.
    """

    store = models.ForeignKey(
        "stores.Store",
        on_delete=models.CASCADE,
        related_name="menus",
        verbose_name="Store",
    )
    name = models.CharField(max_length=100, verbose_name="Menu Name")
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name="Slug",
        help_text="URL-friendly version of the name",
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name="Is Default",
        help_text="Use as the default navigation menu",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        verbose_name = "Menu"
        verbose_name_plural = "Menus"
        unique_together = ["store", "slug"]
        ordering = ["name"]

    def __str__(self):
        return f"{self.store.name} - {self.name}"

    def save(self, *args, **kwargs):
        # Generate slug from name if not provided
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            # Ensure unique slug within store
            while Menu.objects.filter(store=self.store, slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)


class MenuItem(models.Model):
    """
    Individual menu item within a navigation menu.

    Can link to a page or a raw URL, and supports nested structure
    through self-referencing parent relationship.
    """

    menu = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Menu",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="Parent Item",
        help_text="Parent menu item for nested structure",
    )
    title = models.CharField(max_length=100, verbose_name="Title")
    url = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name="URL",
        help_text="External URL or internal path",
    )
    page = models.ForeignKey(
        "posts.Post",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="menu_items",
        verbose_name="Page",
        help_text="Link to a page (alternative to URL)",
    )
    position = models.PositiveIntegerField(
        default=0,
        verbose_name="Position",
        help_text="Order within the menu",
    )
    is_visible = models.BooleanField(
        default=True,
        verbose_name="Is Visible",
        help_text="Show this item in the navigation",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        verbose_name = "Menu Item"
        verbose_name_plural = "Menu Items"
        ordering = ["position", "created_at"]
        unique_together = ["menu", "position", "parent"]

    def __str__(self):
        return f"{self.menu.name} - {self.title}"

    def clean(self):
        # Validate that either page or url is provided, but not both
        if self.page and self.url:
            raise ValidationError("A menu item can have either a page or a URL, but not both.")

        if not self.page and not self.url:
            raise ValidationError("A menu item must have either a page or a URL.")

        # Validate that page is actually a page (not other post types)
        if self.page and self.page.post_type.slug != "page":
            raise ValidationError("Only pages can be linked to menu items.")

        # Validate parent belongs to same menu
        if self.parent and self.parent.menu != self.menu:
            raise ValidationError("Parent menu item must belong to the same menu.")

        # Prevent circular references
        if self.parent and self._is_circular_reference():
            raise ValidationError("Circular reference detected in menu items.")

    def _is_circular_reference(self):
        """Check if setting this parent would create a circular reference."""
        if not self.parent:
            return False

        current = self.parent
        visited = set()

        while current and current.id not in visited:
            visited.add(current.id)
            if current.id == self.id:
                return True
            current = current.parent

        return False

    def get_link(self):
        """Get the actual link for this menu item."""
        if self.page:
            return (
                self.page.get_absolute_url()
                if hasattr(self.page, "get_absolute_url")
                else f"/pages/{self.page.slug}/"
            )
        return self.url

    def get_link_type(self):
        """Get the type of link: 'page' or 'url'."""
        return "page" if self.page else "url"
