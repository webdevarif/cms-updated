"""
Media utilities for Digital Farmers CMS.

This module provides deprecated helper functions that have been moved to MediaService.
Please use apps.mediafile.services.media_service.MediaService directly instead.

DEPRECATED: This module will be removed in a future version.
"""

import logging

logger = logging.getLogger(__name__)


def upload_to_mediafile(*args, **kwargs):
    """
    DEPRECATED: Use MediaService.upload_from_request() instead.

    This function has been moved to MediaService for better organization.
    """
    logger.warning(
        "upload_to_mediafile is deprecated. "
        "Use apps.mediafile.services.media_service.MediaService.upload_from_request() instead."
    )
    from apps.mediafile.services.media_service import MediaService

    service = MediaService()
    return service.upload_from_request(*args, **kwargs)


def get_mediafile_url(*args, **kwargs):
    """
    DEPRECATED: Use MediaService.get_media_url() instead.

    This function has been moved to MediaService for better organization.
    """
    logger.warning(
        "get_mediafile_url is deprecated. "
        "Use apps.mediafile.services.media_service.MediaService.get_media_url() instead."
    )
    from apps.mediafile.services.media_service import MediaService

    service = MediaService()
    return service.get_media_url(*args, **kwargs)


def get_mediafile_thumbnail(*args, **kwargs):
    """
    DEPRECATED: Use MediaService.get_thumbnail_url() instead.

    This function has been moved to MediaService for better organization.
    """
    logger.warning(
        "get_mediafile_thumbnail is deprecated. "
        "Use apps.mediafile.services.media_service.MediaService.get_thumbnail_url() instead."
    )
    from apps.mediafile.services.media_service import MediaService

    service = MediaService()
    return service.get_thumbnail_url(*args, **kwargs)
