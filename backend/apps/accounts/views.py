import logging
from apps.common.throttles import AuthRateThrottle
from apps.common.recaptcha import verify_recaptcha
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import status
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.html import strip_tags
from .models import CustomUser, PatientProfile, DoctorProfile, RelativeInvitation
from .permissions import IsDoctor, IsAdminUser
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    PatientProfileSerializer,
    DoctorProfileSerializer,
    ChangePasswordSerializer,
    InviteRelativeSerializer,
    VerifyInvitationSerializer,
    RegisterRelativeSerializer,
    RelativeInvitationListSerializer,
)

logger = logging.getLogger(__name__)


class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
            },
            status=status.HTTP_201_CREATED,
        )

    def create(self, request, *args, **kwargs):
        if not verify_recaptcha(request.data.get('recaptcha_token'), 'register'):
            return Response(
                {'error': 'Bot korumasi dogrulanamadi. Sayfayi yenileyip tekrar deneyin.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().create(request, *args, **kwargs)



class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        if not verify_recaptcha(request.data.get('recaptcha_token'), 'login'):
            return Response(
                {'error': 'Bot korumasi dogrulanamadi.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        user.last_active = timezone.now()
        user.save(update_fields=['last_active'])
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
            }
        )


class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            pass
        return Response(status=status.HTTP_205_RESET_CONTENT)


class ChangePasswordView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({'detail': 'Password updated successfully.'})


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class PatientProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = PatientProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return PatientProfile.objects.get(user=self.request.user)


class DoctorProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = DoctorProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return DoctorProfile.objects.get(user=self.request.user)


# ==================== RELATIVE INVITATION ====================

INVITATION_EMAIL_TEMPLATE = """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f4f5f7;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f5f7;padding:32px 0">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.1)">
  <tr><td style="background:linear-gradient(135deg,#0d9488,#0891b2);padding:24px 32px">
    <h1 style="margin:0;color:#fff;font-size:20px;font-weight:600">Norosera</h1>
    <p style="margin:4px 0 0;color:rgba(255,255,255,0.85);font-size:13px">Hasta Yakin Takip Sistemi</p>
  </td></tr>
  <tr><td style="padding:32px">
    <h2 style="margin:0 0 12px;color:#1f2937;font-size:18px;font-weight:600">{title}</h2>
    <p style="margin:0 0 24px;color:#4b5563;font-size:15px;line-height:1.6">{message}</p>
    <div style="text-align:center;margin:24px 0">
      <a href="{invite_url}" style="display:inline-block;background:linear-gradient(135deg,#0d9488,#0891b2);color:#fff;padding:14px 32px;border-radius:8px;text-decoration:none;font-size:15px;font-weight:600">Daveti Kabul Et ve Kayit Ol</a>
    </div>
    <p style="margin:16px 0 0;color:#9ca3af;font-size:13px">Bu link 48 saat gecerlidir. Suresi doldugunda yeni bir davet isteyebilirsiniz.</p>
    <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0">
    <p style="margin:0;color:#9ca3af;font-size:12px">Bu e-posta Norosera platformu tarafindan gonderilmistir. Eger bu daveti beklemiyorsaniz, lutfen gormezden gelin.</p>
  </td></tr>
  <tr><td style="background:#f9fafb;padding:16px 32px;text-align:center">
    <p style="margin:0;color:#9ca3af;font-size:11px">&copy; 2026 Norosera - Noroloji Klinigi</p>
  </td></tr>
</table>
</td></tr>
</table>
</body>
</html>"""


class InviteRelativeView(APIView):
    """
    Doctor/caregiver/admin creates an invitation for a patient relative.
    Sends an email with a unique invitation link.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Only doctor, admin, or caregiver can invite
        if request.user.role not in ('doctor', 'admin', 'caregiver'):
            return Response(
                {'error': 'Yalnizca doktor, admin veya bakici davet olusturabilir.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = InviteRelativeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        invitation = RelativeInvitation.objects.create(
            invited_by=request.user,
            patient_id=serializer.validated_data['patient_id'],
            invited_email=serializer.validated_data['invited_email'],
            invited_name=serializer.validated_data.get('invited_name', ''),
            relationship_type=serializer.validated_data['relationship_type'],
        )

        # Send invitation email
        site_url = getattr(settings, 'SITE_URL', 'http://localhost:3000')
        invite_url = f"{site_url}/tr/auth/register-relative?token={invitation.token}"
        patient_name = invitation.patient.get_full_name()
        inviter_name = request.user.get_full_name()

        title = 'Hasta Yakin Takip Daveti'
        message = (
            f"Sayin {invitation.invited_name or invitation.invited_email},<br><br>"
            f"<strong>{inviter_name}</strong> sizi <strong>{patient_name}</strong> hastasinin "
            f"uzaktan takip sistemine davet etti.<br><br>"
            f"Bu davet ile Norosera platformuna kayit olarak hastanizin durumunu "
            f"(bilissel degerlendirmeler, bakici notlari, uyarilar) guvenlice takip edebilirsiniz."
        )

        try:
            html = INVITATION_EMAIL_TEMPLATE.format(
                title=title,
                message=message,
                invite_url=invite_url,
            )
            send_mail(
                subject='[Norosera] Hasta Yakin Takip Daveti',
                message=strip_tags(f"{title}\n\n{message}\n\nDavet linki: {invite_url}"),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[invitation.invited_email],
                html_message=html,
                fail_silently=False,
            )
            email_sent = True
        except Exception as e:
            logger.error(f"Invitation email failed: {e}")
            email_sent = False

        return Response({
            'id': str(invitation.id),
            'token': str(invitation.token),
            'invited_email': invitation.invited_email,
            'patient_name': patient_name,
            'invite_url': invite_url,
            'email_sent': email_sent,
            'expires_at': invitation.expires_at.isoformat(),
        }, status=status.HTTP_201_CREATED)


class InviteRelativeListView(APIView):
    """List all invitations created by the current doctor/caregiver for a patient."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role not in ('doctor', 'admin', 'caregiver'):
            return Response(
                {'error': 'Yetkisiz erisim.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        patient_id = request.query_params.get('patient_id')
        qs = RelativeInvitation.objects.select_related('patient', 'invited_by')

        if patient_id:
            qs = qs.filter(patient_id=patient_id)

        # Doctor sees only their invitations, admin sees all
        if request.user.role != 'admin':
            qs = qs.filter(invited_by=request.user)

        serializer = RelativeInvitationListSerializer(qs[:50], many=True)
        return Response(serializer.data)


class VerifyInvitationView(APIView):
    """Public endpoint to verify an invitation token and return basic info."""
    permission_classes = [AllowAny]

    def get(self, request, token):
        try:
            invitation = RelativeInvitation.objects.select_related('patient', 'invited_by').get(
                token=token
            )
        except RelativeInvitation.DoesNotExist:
            return Response(
                {'error': 'Gecersiz davet linki.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if invitation.is_used:
            return Response(
                {'error': 'Bu davet linki zaten kullanilmis.', 'status': 'used'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if timezone.now() > invitation.expires_at:
            return Response(
                {'error': 'Davet linkinin suresi dolmus.', 'status': 'expired'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({
            'status': 'valid',
            'invited_email': invitation.invited_email,
            'invited_name': invitation.invited_name,
            'patient_first_name': invitation.patient.first_name,
            'relationship_type': invitation.relationship_type,
            'invited_by_name': invitation.invited_by.get_full_name(),
            'expires_at': invitation.expires_at.isoformat(),
        })


class RegisterRelativeView(APIView):
    """Public endpoint for relatives to register using an invitation token."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterRelativeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
        }, status=status.HTTP_201_CREATED)
