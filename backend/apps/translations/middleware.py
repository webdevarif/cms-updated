"""
Translation middleware.

NOTE: This middleware is currently unused and not configured in settings.
It provides request/response translation handling and can be enabled in the future
if translation middleware functionality is needed.
"""

import re

from django.conf import settings
from django.utils import translation


class TranslationMiddleware:
    """Handles request/response translation"""

    def __init__(self, get_response):
        self.get_response = get_response
        self.ignore_paths = [
            r"^/admin/",
            r"^/static/",
            r"^/media/",
            r"^/api/",
            r"\.(js|css|jpg|jpeg|png|gif|ico|svg|woff|ttf|eot|webp|mp4|webm|mp3|wav|ogg|json|xml|csv)$",
        ]

    def __call__(self, request):
        # Set language from request
        self.set_language(request)

        # Process response
        response = self.get_response(request)

        # Skip translation for certain paths/content types
        if self.should_skip_translation(request, response):
            return response

        # Parse and translate response
        return self.translate_response(request, response)

    def set_language(self, request):
        """Set language from request"""
        language = self.get_language_from_request(request)
        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()

    def get_language_from_request(self, request):
        """Get language with store fallback"""
        # 1. URL parameter
        if "lang" in request.GET:
            return request.GET["lang"]

        # 2. Session
        if hasattr(request, "session") and "django_language" in request.session:
            return request.session["django_language"]

        # 3. Store default
        store = getattr(request, "store", None)
        if store and hasattr(store, "default_language") and store.default_language:
            return store.default_language.code

        # 4. Accept-Language header
        if "HTTP_ACCEPT_LANGUAGE" in request.META:
            try:
                language = request.META["HTTP_ACCEPT_LANGUAGE"].split(",")[0].split(";")[0].strip()
            except (AttributeError, IndexError):
                language = None
            try:
                return translation.get_supported_language_variant(language)
            except LookupError:
                pass

        # 5. Default from settings
        return settings.LANGUAGE_CODE

    def should_skip_translation(self, request, response):
        """Check if translation should be skipped"""
        path = request.path

        # Check ignore paths
        for pattern in self.ignore_paths:
            if re.match(pattern, path):
                return True

        # Check content type
        content_type = response.get("Content-Type", "")
        if content_type.startswith(("image/", "video/", "audio/", "application/")):
            return True

        return False

    def translate_response(self, request, response):
        """Translate response content"""
        if response.get("Content-Type", "").startswith("text/html"):
            from .utils.translation_parser import TranslationParser

            parser = TranslationParser(
                store=getattr(request, "store", None),
                language_code=request.LANGUAGE_CODE,
            )

            translated_content = parser.parse_html(response.content.decode("utf-8"))
            response.content = translated_content.encode("utf-8")

        return response
