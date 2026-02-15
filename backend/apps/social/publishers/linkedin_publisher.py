"""
LinkedIn Posts API Publisher.
Organization page uzerinden icerik yayinlama.
"""

import requests
import logging
from .base import BasePublisher, PublishResult

logger = logging.getLogger(__name__)

LINKEDIN_API_BASE = 'https://api.linkedin.com/rest'
LINKEDIN_API_VERSION = '202601'  # YYYYMM format


class LinkedInPublisher(BasePublisher):
    """LinkedIn Posts API ile icerik yayinlama."""

    platform = 'linkedin'

    def __init__(self, social_account):
        super().__init__(social_account)
        self.org_urn = social_account.organization_urn  # 'urn:li:organization:XXXX'

    @property
    def _headers(self):
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0',
            'Linkedin-Version': LINKEDIN_API_VERSION,
        }

    def publish_text(self, text: str) -> PublishResult:
        """LinkedIn'e metin postu paylas."""
        try:
            payload = {
                'author': self.org_urn,
                'commentary': text,
                'visibility': 'PUBLIC',
                'distribution': {
                    'feedDistribution': 'MAIN_FEED',
                    'targetEntities': [],
                    'thirdPartyDistributionChannels': [],
                },
                'lifecycleState': 'PUBLISHED',
                'isReshareDisabledByAuthor': False,
            }

            resp = requests.post(
                f'{LINKEDIN_API_BASE}/posts',
                headers=self._headers,
                json=payload,
                timeout=30
            )

            if resp.status_code == 201:
                post_id = resp.headers.get('x-restli-id', '')
                post_url = f'https://www.linkedin.com/feed/update/{post_id}/' if post_id else ''
                return PublishResult(
                    success=True,
                    platform_post_id=post_id,
                    platform_url=post_url,
                    response_data={'status_code': 201, 'post_id': post_id}
                )
            else:
                return PublishResult(
                    success=False,
                    error=f'LinkedIn API {resp.status_code}: {resp.text[:500]}',
                    response_data={'status_code': resp.status_code, 'body': resp.text[:500]}
                )
        except Exception as e:
            return PublishResult(success=False, error=str(e))

    def publish_single_image(self, image_url: str, caption: str) -> PublishResult:
        """
        LinkedIn'e gorsel ile post paylas.
        1) Image upload (register + PUT binary)
        2) Post olustur (image URN ile)
        """
        try:
            # Step 1: Upload image
            image_urn = self._upload_image(image_url)
            if not image_urn:
                return PublishResult(success=False, error='LinkedIn gorsel yuklenemedi')

            # Step 2: Post olustur
            payload = {
                'author': self.org_urn,
                'commentary': caption,
                'visibility': 'PUBLIC',
                'distribution': {
                    'feedDistribution': 'MAIN_FEED',
                    'targetEntities': [],
                    'thirdPartyDistributionChannels': [],
                },
                'content': {
                    'media': {
                        'id': image_urn,
                    }
                },
                'lifecycleState': 'PUBLISHED',
                'isReshareDisabledByAuthor': False,
            }

            resp = requests.post(
                f'{LINKEDIN_API_BASE}/posts',
                headers=self._headers,
                json=payload,
                timeout=30
            )

            if resp.status_code == 201:
                post_id = resp.headers.get('x-restli-id', '')
                return PublishResult(
                    success=True,
                    platform_post_id=post_id,
                    platform_url=f'https://www.linkedin.com/feed/update/{post_id}/' if post_id else '',
                    response_data={'status_code': 201}
                )
            return PublishResult(success=False, error=f'Post publish failed: {resp.status_code}')
        except Exception as e:
            return PublishResult(success=False, error=str(e))

    def publish_carousel(self, image_urls: list, caption: str) -> PublishResult:
        """LinkedIn MultiImage post."""
        try:
            image_urns = []
            for url in image_urls[:20]:  # LinkedIn max 20
                urn = self._upload_image(url)
                if urn:
                    image_urns.append({'id': urn, 'altText': ''})

            if len(image_urns) < 2:
                return PublishResult(success=False, error='En az 2 gorsel yuklenmeliydi')

            payload = {
                'author': self.org_urn,
                'commentary': caption,
                'visibility': 'PUBLIC',
                'distribution': {
                    'feedDistribution': 'MAIN_FEED',
                    'targetEntities': [],
                    'thirdPartyDistributionChannels': [],
                },
                'content': {
                    'multiImage': {
                        'images': image_urns
                    }
                },
                'lifecycleState': 'PUBLISHED',
                'isReshareDisabledByAuthor': False,
            }

            resp = requests.post(f'{LINKEDIN_API_BASE}/posts', headers=self._headers, json=payload, timeout=30)

            if resp.status_code == 201:
                post_id = resp.headers.get('x-restli-id', '')
                return PublishResult(
                    success=True,
                    platform_post_id=post_id,
                    platform_url=f'https://www.linkedin.com/feed/update/{post_id}/'
                )
            return PublishResult(success=False, error=f'MultiImage publish failed: {resp.status_code}')
        except Exception as e:
            return PublishResult(success=False, error=str(e))

    def validate_token(self) -> bool:
        try:
            resp = requests.get(
                f'{LINKEDIN_API_BASE}/me',
                headers=self._headers,
                timeout=10
            )
            return resp.status_code == 200
        except Exception:
            return False

    def _upload_image(self, image_url: str) -> str:
        """
        LinkedIn'e gorsel yukle, image URN dondur.
        1) Register upload
        2) Gorseli indir
        3) PUT ile yukle
        """
        try:
            # 1. Register
            register_resp = requests.post(
                f'{LINKEDIN_API_BASE}/images?action=initializeUpload',
                headers=self._headers,
                json={
                    'initializeUploadRequest': {
                        'owner': self.org_urn,
                    }
                },
                timeout=15
            )
            register_data = register_resp.json()
            upload_url = register_data.get('value', {}).get('uploadUrl', '')
            image_urn = register_data.get('value', {}).get('image', '')

            if not upload_url or not image_urn:
                logger.error(f'LinkedIn image register failed: {register_data}')
                return ''

            # 2. Gorseli indir
            img_resp = requests.get(image_url, timeout=30)
            if img_resp.status_code != 200:
                return ''

            # 3. Yukle
            upload_resp = requests.put(
                upload_url,
                headers={
                    'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': 'application/octet-stream',
                },
                data=img_resp.content,
                timeout=60
            )

            if upload_resp.status_code in (200, 201):
                return image_urn
            return ''
        except Exception as e:
            logger.error(f'LinkedIn image upload error: {e}')
            return ''
