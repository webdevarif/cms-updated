"""
Base channel class for notifications.
"""
from abc import ABC, abstractmethod


class BaseChannel(ABC):
    """Base channel class"""
    
    @staticmethod
    @abstractmethod
    def send(notification):
        """Send notification via this channel"""
        pass
    
    @staticmethod
    @abstractmethod
    def validate_config(notification):
        """Validate channel configuration"""
        pass
