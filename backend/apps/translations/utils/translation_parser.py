"""
Translation parser utility.
"""
import hashlib

import bleach
from bs4 import BeautifulSoup, NavigableString
from django.conf import settings
from django.core.cache import caches


class TranslationParser:
    """Parses and translates HTML content"""

    def __init__(self, store=None, language_code=None, user=None):
        self.store = store
        self.language_code = language_code or getattr(settings, "LANGUAGE_CODE", "en")
        self.user = user
        self.cache = caches["translations"]

    def parse_html(self, html_content, cache_key=None):
        """Parse and translate HTML content with caching"""
        if not html_content:
            return html_content

        if not cache_key and self.store:
            cache_key = self._generate_cache_key(html_content)
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached

        soup = BeautifulSoup(html_content, "html.parser")
        self._process_nodes(soup)

        result = str(soup)
        if cache_key:
            self.cache.set(cache_key, result, timeout=3600)

        return result

    def _process_nodes(self, soup):
        """Process all translatable nodes"""
        for text_node in self._find_translatable_text_nodes(soup):
            self._process_text_node(text_node)

        for tag in soup.find_all(attrs=True):
            self._process_attributes(tag)

    def _process_text_node(self, text_node):
        """Process a single text node with XSS protection"""
        original = text_node.string.strip()
        if not original or len(original) < 2:
            return

        # Sanitize HTML content
        if "<" in original:
            allowed_tags = getattr(settings, "BLEACH_ALLOWED_TAGS", [])
            allowed_attrs = getattr(settings, "BLEACH_ALLOWED_ATTRIBUTES", [])
            original = bleach.clean(original, tags=allowed_tags, attributes=allowed_attrs)

        # Get or create translation key
        key = self._get_or_create_key(original)

        # Get translation
        translation = self._get_translation(key, original)
        if translation and translation.text != original:
            text_node.replace_with(translation.text)

    def _find_translatable_text_nodes(self, soup):
        """Find text nodes that should be translated"""
        for node in soup.find_all(string=True):
            if isinstance(node, NavigableString):
                # Skip if inside script/style tags
                parent = node.parent
                if parent and parent.name in ["script", "style", "code", "pre"]:
                    continue
                yield node

    def _process_attributes(self, tag):
        """Process translatable attributes"""
        translatable_attrs = ["title", "alt", "placeholder"]
        for attr in translatable_attrs:
            if tag.has_attr(attr):
                value = tag.get(attr)
                if value and len(value) > 1:
                    translation = self._get_translation_for_text(value)
                    if translation:
                        tag[attr] = translation

    def _generate_cache_key(self, content):
        """Generate cache key for content"""
        content_hash = hashlib.md5(content.encode()).hexdigest()
        return (
            f"trans:{self.store.id if self.store else 'global'}:{self.language_code}:{content_hash}"
        )

    def _get_or_create_key(self, text):
        """Get or create translation key"""
        from ..models import TranslationKey

        key, created = TranslationKey.objects.get_or_create(
            key=text[:255],
            defaults={"namespace": "default", "content_type": "plain", "plural_form": "none"},
        )

        return key

    def _get_translation(self, key, original_text):
        """Get translation for key"""
        from ..models import Translation

        try:
            translation = Translation.objects.get(
                key=key, language__code=self.language_code, store=self.store
            )
            return translation
        except Translation.DoesNotExist:
            return None

    def _get_translation_for_text(self, text):
        """Get translation for arbitrary text"""
        key = self._get_or_create_key(text)
        return self._get_translation(key, text)
