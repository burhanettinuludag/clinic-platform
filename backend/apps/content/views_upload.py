"""
Image upload endpoint.
POST /api/v1/content/upload-image/

Desteklenen formatlar: JPEG, PNG, WebP, GIF
Max boyut: 5MB
Otomatik resize: max 1920px genislik
"""

import os
import uuid
import logging
from PIL import Image as PILImage
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from apps.accounts.permissions import IsDoctor

logger = logging.getLogger(__name__)

ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
MAX_SIZE = 5 * 1024 * 1024  # 5MB
MAX_WIDTH = 1920


class ImageUploadView(APIView):
    """Makale/haber icin gorsel yukleme."""
    permission_classes = [IsAuthenticated, IsDoctor]
    parser_classes = [MultiPartParser]

    def post(self, request):
        file = request.FILES.get('image')
        if not file:
            return Response({'error': 'Gorsel dosyasi zorunludur.'}, status=400)

        # Tip kontrol
        if file.content_type not in ALLOWED_TYPES:
            return Response(
                {'error': f'Desteklenmeyen format. Izin verilen: JPEG, PNG, WebP, GIF'},
                status=400,
            )

        # Boyut kontrol
        if file.size > MAX_SIZE:
            return Response({'error': 'Dosya boyutu 5MB\'dan buyuk olamaz.'}, status=400)

        # Hedef klasor
        upload_type = request.data.get('type', 'articles')  # articles, news_images
        if upload_type not in ('articles', 'news_images', 'general'):
            upload_type = 'articles'

        # Unique dosya adi
        ext = os.path.splitext(file.name)[1].lower() or '.jpg'
        if ext not in ('.jpg', '.jpeg', '.png', '.webp', '.gif'):
            ext = '.jpg'
        filename = f"{uuid.uuid4().hex[:12]}{ext}"

        # Klasoru olustur
        upload_dir = os.path.join(settings.MEDIA_ROOT, upload_type)
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, filename)

        # Resize ve kaydet
        try:
            img = PILImage.open(file)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')

            # Max genislik resize
            if img.width > MAX_WIDTH:
                ratio = MAX_WIDTH / img.width
                new_h = int(img.height * ratio)
                img = img.resize((MAX_WIDTH, new_h), PILImage.LANCZOS)

            # Kaydet
            quality = 85 if ext in ('.jpg', '.jpeg') else 90
            img.save(filepath, quality=quality, optimize=True)

            url = f"{settings.MEDIA_URL}{upload_type}/{filename}"
            logger.info(f"Image uploaded: {url} by {request.user.email}")

            return Response({
                'success': True,
                'url': url,
                'filename': filename,
                'width': img.width,
                'height': img.height,
                'size': os.path.getsize(filepath),
            })

        except Exception as e:
            logger.error(f"Image upload error: {e}")
            # Temizle
            if os.path.exists(filepath):
                os.remove(filepath)
            return Response({'error': 'Gorsel isleme hatasi.'}, status=500)
