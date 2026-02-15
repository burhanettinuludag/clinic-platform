from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import ConsentRecord
from .serializers import ConsentRecordSerializer, GrantConsentSerializer


class ConsentListView(generics.ListAPIView):
    """Kullanıcının tüm rıza kayıtlarını listeler."""
    permission_classes = [IsAuthenticated]
    serializer_class = ConsentRecordSerializer

    def get_queryset(self):
        return ConsentRecord.objects.filter(user=self.request.user)


class GrantConsentView(generics.GenericAPIView):
    """Rıza ver veya geri çek."""
    permission_classes = [IsAuthenticated]
    serializer_class = GrantConsentSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        consent_type = serializer.validated_data['consent_type']
        version = serializer.validated_data['version']
        granted = serializer.validated_data['granted']

        def get_client_ip():
            x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded:
                return x_forwarded.split(',')[0].strip()
            return request.META.get('REMOTE_ADDR')

        record, created = ConsentRecord.objects.update_or_create(
            user=request.user,
            consent_type=consent_type,
            version=version,
            defaults={
                'granted': granted,
                'granted_at': timezone.now() if granted else None,
                'revoked_at': timezone.now() if not granted else None,
                'ip_address': get_client_ip(),
                'user_agent': request.META.get('HTTP_USER_AGENT', '')[:500],
            },
        )

        return Response(
            ConsentRecordSerializer(record).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.permissions import AllowAny
from django.core.mail import send_mail
from django.conf import settings


class ContactSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    subject = serializers.CharField(max_length=200)
    message = serializers.CharField(max_length=2000)
    recaptcha_token = serializers.CharField(required=False, allow_blank=True)


class ContactView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = 'anon'

    def post(self, request):
        s = ContactSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        try:
            send_mail(
                subject=f"[Norosera Iletisim] {d['subject']}",
                message=f"Gonderen: {d['name']} ({d['email']})\n\n{d['message']}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[getattr(settings, 'CONTACT_EMAIL', 'info@norosera.com')],
                fail_silently=True,
            )
        except Exception:
            pass
        return Response({'detail': 'Mesajiniz alindi. En kisa surede donus yapacagiz.'}, status=status.HTTP_200_OK)
