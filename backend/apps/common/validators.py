"""
Dosya yukleme guvenlik validatorleri.
Tum modellerdeki FileField/ImageField alanlari icin kullanilir.
"""
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator


# --- Izin verilen uzantilar ---
ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']
ALLOWED_DOCUMENT_EXTENSIONS = ['pdf', 'doc', 'docx']

# --- Boyut limitleri ---
MAX_IMAGE_SIZE = 5 * 1024 * 1024       # 5 MB
MAX_DOCUMENT_SIZE = 10 * 1024 * 1024    # 10 MB


def validate_image_file_size(value):
    """Gorsel dosya boyutu 5 MB'yi gecemez."""
    if value.size > MAX_IMAGE_SIZE:
        raise ValidationError(
            f'Gorsel dosya boyutu en fazla 5 MB olabilir. '
            f'Yuklenen dosya: {value.size / (1024 * 1024):.1f} MB.'
        )


def validate_document_file_size(value):
    """Belge dosya boyutu 10 MB'yi gecemez."""
    if value.size > MAX_DOCUMENT_SIZE:
        raise ValidationError(
            f'Belge dosya boyutu en fazla 10 MB olabilir. '
            f'Yuklenen dosya: {value.size / (1024 * 1024):.1f} MB.'
        )


def validate_file_content_type(value):
    """
    Dosyanin MIME type'ini kontrol et.
    Uzanti degistirilerek yuklenen zararli dosyalari engeller.
    """
    import magic

    # Dosya baslangicini oku
    try:
        file_mime = magic.from_buffer(value.read(2048), mime=True)
        value.seek(0)  # Dosya imlecini basa al
    except Exception:
        return  # magic kurulu degilse sessizce gec

    allowed_mimes = {
        'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml',
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    }

    if file_mime not in allowed_mimes:
        raise ValidationError(
            f'Bu dosya turu kabul edilmiyor: {file_mime}. '
            f'Izin verilen turler: JPG, PNG, GIF, WebP, SVG, PDF, DOC, DOCX.'
        )


# --- Hazir validator listeleri ---
image_validators = [
    FileExtensionValidator(allowed_extensions=ALLOWED_IMAGE_EXTENSIONS),
    validate_image_file_size,
]

document_validators = [
    FileExtensionValidator(allowed_extensions=ALLOWED_DOCUMENT_EXTENSIONS),
    validate_document_file_size,
]
