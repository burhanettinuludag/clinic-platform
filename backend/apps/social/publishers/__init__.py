"""
Publisher factory.
Platform'a gore dogru publisher instance'i dondurur.
"""

from .base import BasePublisher, PublishResult
from .instagram_publisher import InstagramPublisher
from .linkedin_publisher import LinkedInPublisher

_PUBLISHER_MAP = {
    'instagram': InstagramPublisher,
    'linkedin': LinkedInPublisher,
}


def get_publisher(social_account) -> BasePublisher:
    """
    SocialAccount'a gore dogru publisher dondur.
    Desteklenmeyen platform icin ValueError firlatir.
    """
    publisher_cls = _PUBLISHER_MAP.get(social_account.platform)
    if not publisher_cls:
        raise ValueError(f"Desteklenmeyen platform: {social_account.platform}")
    return publisher_cls(social_account)


__all__ = [
    'BasePublisher',
    'PublishResult',
    'InstagramPublisher',
    'LinkedInPublisher',
    'get_publisher',
]
