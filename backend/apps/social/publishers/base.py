"""
Base Publisher — Sosyal medya yayinci base class.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class PublishResult:
    success: bool
    platform_post_id: str = ''
    platform_url: str = ''
    error: str = ''
    response_data: dict = field(default_factory=dict)


class BasePublisher(ABC):
    """Sosyal medya yayinci base class."""

    platform: str = ''

    def __init__(self, social_account):
        self.account = social_account
        self.access_token = social_account.access_token

    @abstractmethod
    def publish_single_image(self, image_url: str, caption: str) -> PublishResult:
        """Tek gorsel paylas."""
        pass

    @abstractmethod
    def publish_carousel(self, image_urls: list, caption: str) -> PublishResult:
        """Carousel/galeri paylas."""
        pass

    @abstractmethod
    def publish_text(self, text: str) -> PublishResult:
        """Sadece metin paylas."""
        pass

    @abstractmethod
    def validate_token(self) -> bool:
        """Token'in gecerli olup olmadigini kontrol et."""
        pass

    def publish(self, post) -> PublishResult:
        """SocialPost objesinden otomatik publish."""
        caption = post.final_caption_with_hashtags

        if post.post_format in ('single_image', 'reel', 'story'):
            if not post.image_urls:
                return PublishResult(success=False, error='Gorsel URL bulunamadi')
            return self.publish_single_image(post.image_urls[0], caption)

        elif post.post_format == 'carousel':
            if len(post.image_urls) < 2:
                return PublishResult(success=False, error='Carousel icin en az 2 gorsel gerekli')
            return self.publish_carousel(post.image_urls, caption)

        elif post.post_format == 'text_only':
            return self.publish_text(caption)

        return PublishResult(success=False, error=f'Desteklenmeyen format: {post.post_format}')
