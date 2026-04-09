from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import CustomUser, PatientProfile, DoctorProfile, RelativeProfile, RelativeInvitation


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    specialty = serializers.CharField(max_length=100, required=False, default='')
    license_number = serializers.CharField(max_length=50, required=False, default='')
    # KVKK consent fields
    consent_kvkk = serializers.BooleanField(write_only=True)
    consent_health_data = serializers.BooleanField(write_only=True, required=False, default=False)
    consent_terms = serializers.BooleanField(write_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'role',
            'phone', 'preferred_language',
            'specialty', 'license_number',
            'consent_kvkk', 'consent_health_data', 'consent_terms',
        ]

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        # Doctor role requires specialty and license_number
        if data.get('role') == CustomUser.Role.DOCTOR:
            if not data.get('specialty'):
                raise serializers.ValidationError({'specialty': 'Uzmanlik alani zorunludur.'})
            if not data.get('license_number'):
                raise serializers.ValidationError({'license_number': 'Diploma/sicil numarasi zorunludur.'})
        # KVKK and terms consent are mandatory
        if not data.get('consent_kvkk'):
            raise serializers.ValidationError({'consent_kvkk': 'KVKK onamı zorunludur.'})
        if not data.get('consent_terms'):
            raise serializers.ValidationError({'consent_terms': 'Kullanım koşulları onayı zorunludur.'})
        # Health data consent mandatory for patients
        if data.get('role') == CustomUser.Role.PATIENT and not data.get('consent_health_data'):
            raise serializers.ValidationError({'consent_health_data': 'Sağlık verisi işleme onayı zorunludur.'})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        specialty = validated_data.pop('specialty', '')
        license_number = validated_data.pop('license_number', '')
        # Extract consent data
        consent_kvkk = validated_data.pop('consent_kvkk', False)
        consent_health_data = validated_data.pop('consent_health_data', False)
        consent_terms = validated_data.pop('consent_terms', False)

        user = CustomUser(**validated_data)
        user.set_password(password)

        # Doctor accounts start as inactive until approved
        if user.role == CustomUser.Role.DOCTOR:
            user.is_active = False

        user.save()

        # Update doctor profile with specialty and license (signal already created it)
        if user.role == CustomUser.Role.DOCTOR and (specialty or license_number):
            try:
                profile = user.doctor_profile
                profile.specialty = specialty
                profile.license_number = license_number
                profile.save(update_fields=['specialty', 'license_number'])
            except DoctorProfile.DoesNotExist:
                pass

        # Create KVKK consent records
        from apps.common.models import ConsentRecord
        request = self.context.get('request')
        ip_address = None
        user_agent = ''
        if request:
            ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
            if ip_address and ',' in ip_address:
                ip_address = ip_address.split(',')[0].strip()
            user_agent = request.META.get('HTTP_USER_AGENT', '')

        now = timezone.now()
        consent_records = [
            ('kvkk', consent_kvkk),
            ('health_data', consent_health_data),
            ('terms', consent_terms),
        ]
        for consent_type, granted in consent_records:
            if granted:
                ConsentRecord.objects.create(
                    user=user,
                    consent_type=consent_type,
                    version='1.0',
                    granted=True,
                    granted_at=now,
                    ip_address=ip_address,
                    user_agent=user_agent[:500],
                )

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        # Check for pending/rejected doctors before authenticate()
        # (authenticate returns None for inactive users, losing context)
        try:
            user_obj = CustomUser.objects.get(email=data['email'])
            if user_obj.role == 'doctor' and not user_obj.is_active:
                # Verify password first so we don't leak user existence
                if user_obj.check_password(data['password']):
                    if hasattr(user_obj, 'doctor_profile'):
                        approval = user_obj.doctor_profile.approval_status
                        if approval == 'pending':
                            raise serializers.ValidationError({
                                'non_field_errors': ['Doktor basvurunuz inceleniyor. Onaylandiktan sonra giris yapabileceksiniz.'],
                                'approval_status': 'pending_approval',
                            })
                        elif approval == 'rejected':
                            raise serializers.ValidationError({
                                'non_field_errors': ['Doktor basvurunuz reddedildi. Detaylar icin destek ile iletisime gecin.'],
                                'approval_status': 'rejected',
                            })
        except CustomUser.DoesNotExist:
            pass

        request = self.context.get('request')
        user = authenticate(request=request, email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError('Invalid email or password.')
        if not user.is_active:
            raise serializers.ValidationError('Account is disabled.')
        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'first_name', 'last_name',
            'role', 'phone', 'preferred_language',
            'is_email_verified', 'date_joined', 'last_active',
        ]
        read_only_fields = ['id', 'email', 'role', 'is_email_verified', 'date_joined']


class PatientProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = PatientProfile
        fields = [
            'id', 'user', 'date_of_birth', 'gender',
            'emergency_contact_name', 'emergency_contact_phone',
        ]
        read_only_fields = ['id']


class DoctorProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = DoctorProfile
        fields = [
            'id', 'user', 'specialty', 'license_number',
            'bio', 'is_accepting_patients', 'approval_status',
        ]
        read_only_fields = ['id', 'approval_status']


class DoctorApplicationSerializer(serializers.ModelSerializer):
    """Serializer for admin to view/manage doctor applications."""
    user = UserSerializer(read_only=True)
    approval_status_display = serializers.CharField(source='get_approval_status_display', read_only=True)

    class Meta:
        model = DoctorProfile
        fields = [
            'id', 'user', 'specialty', 'license_number', 'bio',
            'approval_status', 'approval_status_display',
            'approved_by', 'approved_at', 'rejection_reason',
            'created_at',
        ]
        read_only_fields = ['id', 'approved_by', 'approved_at', 'created_at']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=8)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect.')
        return value


# ==================== RELATIVE INVITATION ====================

class InviteRelativeSerializer(serializers.Serializer):
    """Doctor/caregiver creates an invitation for a patient's relative."""
    patient_id = serializers.UUIDField()
    invited_email = serializers.EmailField()
    invited_name = serializers.CharField(max_length=150, required=False, default='')
    relationship_type = serializers.ChoiceField(
        choices=RelativeProfile.RelationshipType.choices,
        default=RelativeProfile.RelationshipType.OTHER,
    )

    def validate_patient_id(self, value):
        try:
            patient = CustomUser.objects.get(id=value, role='patient')
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError('Hasta bulunamadi.')
        return value

    def validate_invited_email(self, value):
        # Check if a relative with this email is already linked to this patient
        # (will be checked in the view with patient_id)
        return value.lower()

    def validate(self, data):
        # Check if an active invitation already exists for this email+patient combo
        existing = RelativeInvitation.objects.filter(
            invited_email=data['invited_email'],
            patient_id=data['patient_id'],
            is_used=False,
            expires_at__gt=timezone.now(),
        ).exists()
        if existing:
            raise serializers.ValidationError(
                {'invited_email': 'Bu e-posta icin aktif bir davet zaten mevcut.'}
            )

        # Check if user already registered as relative for this patient
        existing_relative = RelativeProfile.objects.filter(
            user__email=data['invited_email'],
            patient_id=data['patient_id'],
        ).exists()
        if existing_relative:
            raise serializers.ValidationError(
                {'invited_email': 'Bu e-posta zaten bu hastanin yakinlari arasinda kayitli.'}
            )
        return data


class VerifyInvitationSerializer(serializers.Serializer):
    """Public endpoint to verify an invitation token."""
    token = serializers.UUIDField()

    def validate_token(self, value):
        try:
            invitation = RelativeInvitation.objects.select_related('patient', 'invited_by').get(
                token=value
            )
        except RelativeInvitation.DoesNotExist:
            raise serializers.ValidationError('Gecersiz davet linki.')

        if invitation.is_used:
            raise serializers.ValidationError('Bu davet linki zaten kullanilmis.')

        if timezone.now() > invitation.expires_at:
            raise serializers.ValidationError('Davet linkinin suresi dolmus.')

        return value


class RegisterRelativeSerializer(serializers.Serializer):
    """Register a new user as a patient relative using an invitation token."""
    token = serializers.UUIDField()
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    phone = serializers.CharField(max_length=20, required=False, default='')

    def validate_token(self, value):
        try:
            invitation = RelativeInvitation.objects.select_related('patient', 'invited_by').get(
                token=value
            )
        except RelativeInvitation.DoesNotExist:
            raise serializers.ValidationError('Gecersiz davet linki.')

        if invitation.is_used:
            raise serializers.ValidationError('Bu davet linki zaten kullanilmis.')

        if timezone.now() > invitation.expires_at:
            raise serializers.ValidationError('Davet linkinin suresi dolmus.')

        return value

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Sifreler eslesmiyor.'})
        return data

    def create(self, validated_data):
        token = validated_data.pop('token')
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')

        invitation = RelativeInvitation.objects.select_related('patient', 'invited_by').get(
            token=token
        )

        # Check if user already exists with this email
        email = invitation.invited_email
        existing_user = CustomUser.objects.filter(email=email).first()
        if existing_user:
            # If user exists but doesn't have a relative profile for this patient
            if hasattr(existing_user, 'relative_profile'):
                raise serializers.ValidationError(
                    {'token': 'Bu e-posta zaten bir yakin hesabi olarak kayitli.'}
                )
            # Can't reuse existing accounts - must use unique email
            raise serializers.ValidationError(
                {'token': 'Bu e-posta adresi zaten kullaniliyor. Farkli bir e-posta ile davet olusturun.'}
            )

        # Create user
        user = CustomUser.objects.create_user(
            email=email,
            password=password,
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone=validated_data.get('phone', ''),
            role=CustomUser.Role.RELATIVE,
            is_email_verified=True,  # Verified via invitation
        )

        # Create relative profile (auto-approved since doctor/caregiver invited)
        RelativeProfile.objects.create(
            user=user,
            patient=invitation.patient,
            relationship_type=invitation.relationship_type,
            is_approved=True,
            approved_by=invitation.invited_by,
            approved_at=timezone.now(),
        )

        # Mark invitation as used
        invitation.is_used = True
        invitation.used_at = timezone.now()
        invitation.save(update_fields=['is_used', 'used_at'])

        return user


class RelativeInvitationListSerializer(serializers.ModelSerializer):
    """For listing invitations in doctor panel."""
    patient_name = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = RelativeInvitation
        fields = [
            'id', 'token', 'invited_email', 'invited_name',
            'relationship_type', 'patient_name',
            'is_used', 'expires_at', 'created_at', 'status',
        ]

    def get_patient_name(self, obj):
        return obj.patient.get_full_name()

    def get_status(self, obj):
        if obj.is_used:
            return 'used'
        if timezone.now() > obj.expires_at:
            return 'expired'
        return 'active'
