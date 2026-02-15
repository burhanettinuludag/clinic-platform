"""
Instagram Graph API Publisher.
2 asamali yayin: container olustur → publish et.
"""

import requests
import time
import logging
from .base import BasePublisher, PublishResult

logger = logging.getLogger(__name__)

GRAPH_API_VERSION = 'v19.0'
GRAPH_API_BASE = f'https://graph.facebook.com/{GRAPH_API_VERSION}'


class InstagramPublisher(BasePublisher):
    """Instagram Graph API ile icerik yayinlama."""

    platform = 'instagram'

    def __init__(self, social_account):
        super().__init__(social_account)
        self.ig_user_id = social_account.account_id

    def publish_single_image(self, image_url: str, caption: str) -> PublishResult:
        """
        Instagram'a tek gorsel paylas.
        2 asamali: container olustur → publish et
        """
        try:
            # Step 1: Media container olustur
            container_url = f'{GRAPH_API_BASE}/{self.ig_user_id}/media'
            container_resp = requests.post(container_url, data={
                'image_url': image_url,
                'caption': caption,
                'access_token': self.access_token,
            }, timeout=30)

            container_data = container_resp.json()
            if 'error' in container_data:
                return PublishResult(
                    success=False,
                    error=f"Container hatasi: {container_data['error'].get('message', '')}",
                    response_data=container_data
                )

            container_id = container_data.get('id')
            if not container_id:
                return PublishResult(success=False, error='Container ID alinamadi', response_data=container_data)

            # Step 2: Container hazir olana kadar bekle
            if not self._wait_for_container(container_id):
                return PublishResult(success=False, error='Container hazirlanamadi (timeout)')

            # Step 3: Publish
            publish_url = f'{GRAPH_API_BASE}/{self.ig_user_id}/media_publish'
            publish_resp = requests.post(publish_url, data={
                'creation_id': container_id,
                'access_token': self.access_token,
            }, timeout=30)

            publish_data = publish_resp.json()
            if 'error' in publish_data:
                return PublishResult(
                    success=False,
                    error=f"Publish hatasi: {publish_data['error'].get('message', '')}",
                    response_data=publish_data
                )

            media_id = publish_data.get('id', '')
            permalink = self._get_permalink(media_id)

            return PublishResult(
                success=True,
                platform_post_id=media_id,
                platform_url=permalink,
                response_data=publish_data
            )

        except requests.Timeout:
            return PublishResult(success=False, error='Instagram API timeout')
        except Exception as e:
            logger.error(f'Instagram publish error: {e}')
            return PublishResult(success=False, error=str(e))

    def publish_carousel(self, image_urls: list, caption: str) -> PublishResult:
        """
        Instagram carousel (galeri) paylas.
        Her gorsel icin ayri container → hepsini birlestir → publish
        """
        try:
            # Step 1: Her gorsel icin child container
            child_ids = []
            for img_url in image_urls[:10]:  # Max 10 gorsel
                resp = requests.post(f'{GRAPH_API_BASE}/{self.ig_user_id}/media', data={
                    'image_url': img_url,
                    'is_carousel_item': 'true',
                    'access_token': self.access_token,
                }, timeout=30)
                data = resp.json()
                if 'id' in data:
                    child_ids.append(data['id'])
                else:
                    logger.warning(f'Carousel child failed: {data}')

            if len(child_ids) < 2:
                return PublishResult(success=False, error='En az 2 carousel item gerekli')

            # Step 2: Carousel container
            resp = requests.post(f'{GRAPH_API_BASE}/{self.ig_user_id}/media', data={
                'caption': caption,
                'media_type': 'CAROUSEL',
                'children': ','.join(child_ids),
                'access_token': self.access_token,
            }, timeout=30)
            container_data = resp.json()
            container_id = container_data.get('id')

            if not container_id:
                return PublishResult(success=False, error='Carousel container olusturulamadi', response_data=container_data)

            # Step 3: Publish
            if not self._wait_for_container(container_id):
                return PublishResult(success=False, error='Container timeout')

            publish_resp = requests.post(f'{GRAPH_API_BASE}/{self.ig_user_id}/media_publish', data={
                'creation_id': container_id,
                'access_token': self.access_token,
            }, timeout=30)
            publish_data = publish_resp.json()

            media_id = publish_data.get('id', '')
            permalink = self._get_permalink(media_id)

            return PublishResult(
                success=True,
                platform_post_id=media_id,
                platform_url=permalink,
                response_data=publish_data
            )
        except Exception as e:
            return PublishResult(success=False, error=str(e))

    def publish_text(self, text: str) -> PublishResult:
        """Instagram text-only desteklemiyor."""
        return PublishResult(success=False, error='Instagram sadece metin paylasimini desteklemiyor')

    def validate_token(self) -> bool:
        """Token gecerlilik kontrolu."""
        try:
            resp = requests.get(f'{GRAPH_API_BASE}/me', params={
                'access_token': self.access_token,
                'fields': 'id,name',
            }, timeout=10)
            return resp.status_code == 200 and 'id' in resp.json()
        except Exception:
            return False

    def refresh_token(self) -> bool:
        """Long-lived token yenile (60 gun)."""
        from django.conf import settings
        try:
            resp = requests.get(f'{GRAPH_API_BASE}/oauth/access_token', params={
                'grant_type': 'fb_exchange_token',
                'client_id': settings.META_APP_ID,
                'client_secret': settings.META_APP_SECRET,
                'fb_exchange_token': self.access_token,
            }, timeout=10)
            data = resp.json()
            if 'access_token' in data:
                self.account.access_token = data['access_token']
                if 'expires_in' in data:
                    from django.utils import timezone
                    from datetime import timedelta
                    self.account.token_expires_at = timezone.now() + timedelta(seconds=data['expires_in'])
                self.account.status = 'active'
                self.account.save()
                return True
        except Exception:
            pass
        return False

    def _wait_for_container(self, container_id, max_wait=30, interval=2):
        """Container FINISHED durumuna gelene kadar bekle."""
        for _ in range(max_wait // interval):
            resp = requests.get(f'{GRAPH_API_BASE}/{container_id}', params={
                'fields': 'status_code',
                'access_token': self.access_token,
            }, timeout=10)
            data = resp.json()
            status = data.get('status_code')
            if status == 'FINISHED':
                return True
            if status == 'ERROR':
                return False
            time.sleep(interval)
        return False

    def _get_permalink(self, media_id):
        """Post permalink'ini al."""
        if not media_id:
            return ''
        try:
            resp = requests.get(f'{GRAPH_API_BASE}/{media_id}', params={
                'fields': 'permalink',
                'access_token': self.access_token,
            }, timeout=10)
            return resp.json().get('permalink', '')
        except Exception:
            return ''
