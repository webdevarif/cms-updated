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
        # Use default cache if translations cache is not configured
        try:
            self.cache = caches["translations"]
        except Exception:
            self.cache = caches["default"]

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
        if not isinstance(text_node, NavigableString):
            return

        text = str(text_node).strip()
        if not text or len(text) < 2:
            return

        # Skip code blocks and preformatted text
        parent = text_node.parent
        if parent and parent.name in ["code", "pre", "script", "style"]:
            return

        # Get translation for this text
        translated = self._get_translation(text)
        if translated and translated != text:
            text_node.replace_with(translated)

    def _process_attributes(self, tag):
        """Process translatable attributes like title, alt, placeholder"""
        translatable_attrs = ["title", "alt", "placeholder", "label"]

        for attr in translatable_attrs:
            if attr in tag.attrs:
                original_value = tag.attrs[attr]
                if original_value and len(original_value.strip()) >= 2:
                    translated = self._get_translation(original_value)
                    if translated and translated != original_value:
                        tag.attrs[attr] = translated

    def _find_translatable_text_nodes(self, soup):
        """Find text nodes that should be translated"""
        # Skip certain tags that shouldn't have their content translated
        skip_tags = ["script", "style", "code", "pre", "noscript"]

        for element in soup.find_all(text=True):
            parent = element.parent
            if parent and parent.name not in skip_tags:
                yield element

    def _get_translation(self, text):
        """Get translation for text (placeholder implementation)"""
        # This is a placeholder - in a real implementation, this would
        # look up translations from a database or translation service

        # For now, just return the original text
        # TODO: Implement actual translation lookup
        return text

    def _generate_cache_key(self, content):
        """Generate cache key for content"""
        content_hash = hashlib.md5(content.encode()).hexdigest()
        store_id = self.store.id if self.store else "global"
        return f"translation:{store_id}:{self.language_code}:{content_hash}"

    @staticmethod
    def clean_html(html_content):
        """Clean HTML content to prevent XSS"""
        if not html_content:
            return html_content

        # Allow basic HTML tags for translation
        allowed_tags = [
            "p",
            "br",
            "strong",
            "em",
            "u",
            "i",
            "b",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "ul",
            "ol",
            "li",
            "a",
            "span",
            "div",
        ]
        allowed_attributes = {
            "a": ["href", "title"],
            "*": ["title", "alt", "class", "id"],
        }

        return bleach.clean(
            html_content, tags=allowed_tags, attributes=allowed_attributes, strip=True
        )
