from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        # Beklenmeyen hata - detayları logla ama kullanıcıya gösterme
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return Response(
            {'error': 'Bir hata olustu. Lutfen daha sonra tekrar deneyin.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # Stack trace veya debug bilgisi sızdırmamak için response'u temizle
    if response.status_code >= 500:
        response.data = {'error': 'Sunucu hatasi.'}

    return response
