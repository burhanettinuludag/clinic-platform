from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import CustomUser, PatientProfile, DoctorProfile, RelativeProfile, RelativeInvitation


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'role',
            'phone', 'preferred_language',
        ]

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
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
            'bio', 'is_accepting_patients',
        ]
        read_only_fields = ['id']


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
