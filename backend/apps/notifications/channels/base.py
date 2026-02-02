"""
Base channel class for notifications.

This module defines the interface that all notification channels must implement.
Each channel (email, in_app, push, sms) should inherit from BaseChannel and implement
the required methods for notification delivery and configuration validation.
"""

from abc import ABC, abstractmethod


class BaseChannel(ABC):
    """
    Base interface for all notification channels.

    This class defines the contract that all notification channels must follow.
    Each channel implementation should inherit from this class and implement
    the required methods for delivering notifications and validating configuration.

    Expected methods:
    - send(notification): Deliver notification via the channel
    - validate_config(notification): Validate channel-specific configuration

    Return values/exceptions:
    - send() should return success/failure status or raise appropriate exceptions
    - validate_config() should return True/False or raise ValidationError
    """

    @staticmethod
    @abstractmethod
    def send(notification):
        """
        Send notification via this channel.

        Args:
            notification: Notification instance to send

        Returns:
            bool or dict: Success status or delivery result details

        Raises:
            ChannelError: If delivery fails due to channel-specific issues
        """
        pass

    @staticmethod
    @abstractmethod
    def validate_config(notification):
        """
        Validate channel configuration for the notification.

        Args:
            notification: Notification instance to validate

        Returns:
            bool: True if configuration is valid

        Raises:
            ValidationError: If configuration is invalid
        """
        pass
