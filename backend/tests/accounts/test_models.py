"""
Unit tests for accounts models.
"""

import pytest
from django.db import IntegrityError
from apps.accounts.models import CustomUser, PatientProfile, DoctorProfile


@pytest.mark.django_db
class TestCustomUser:
    """Tests for CustomUser model."""

    def test_create_user(self, user_factory):
        """Test creating a regular user."""
        user = user_factory(email='newuser@example.com')
        assert user.email == 'newuser@example.com'
        assert user.role == 'patient'
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_create_user_without_email_raises_error(self):
        """Test that creating user without email raises ValueError."""
        with pytest.raises(ValueError, match='Email is required'):
            CustomUser.objects.create_user(email='', password='test123')

    def test_create_superuser(self):
        """Test creating a superuser."""
        admin = CustomUser.objects.create_superuser(
            email='superadmin@example.com',
            password='adminpass123',
            first_name='Super',
            last_name='Admin'
        )
        assert admin.is_staff is True
        assert admin.is_superuser is True
        assert admin.role == CustomUser.Role.ADMIN

    def test_email_is_unique(self, user_factory):
        """Test that email must be unique."""
        user_factory(email='unique@example.com')
        with pytest.raises(IntegrityError):
            user_factory(email='unique@example.com')

    def test_user_str_representation(self, patient_user):
        """Test user string representation."""
        expected = f"{patient_user.get_full_name()} ({patient_user.email})"
        assert str(patient_user) == expected

    def test_user_roles(self, patient_user, doctor_user, admin_user):
        """Test different user roles."""
        assert patient_user.role == CustomUser.Role.PATIENT
        assert doctor_user.role == CustomUser.Role.DOCTOR
        assert admin_user.role == CustomUser.Role.ADMIN


@pytest.mark.django_db
class TestPatientProfile:
    """Tests for PatientProfile model."""

    def test_create_patient_profile(self, patient_profile):
        """Test creating a patient profile."""
        assert patient_profile.user is not None
        assert patient_profile.gender == 'male'
        assert patient_profile.emergency_contact_name == 'Emergency Contact'

    def test_patient_profile_str(self, patient_profile):
        """Test patient profile string representation."""
        expected = f"Patient: {patient_profile.user.get_full_name()}"
        assert str(patient_profile) == expected

    def test_patient_can_have_assigned_doctor(self, patient_profile, doctor_user):
        """Test that patient can be assigned to a doctor."""
        patient_profile.assigned_doctor = doctor_user
        patient_profile.save()
        patient_profile.refresh_from_db()
        assert patient_profile.assigned_doctor == doctor_user


@pytest.mark.django_db
class TestDoctorProfile:
    """Tests for DoctorProfile model."""

    def test_create_doctor_profile(self, doctor_profile):
        """Test creating a doctor profile."""
        assert doctor_profile.user is not None
        assert doctor_profile.specialty == 'Neurology'
        assert doctor_profile.license_number == 'DOC12345'
        assert doctor_profile.is_accepting_patients is True

    def test_doctor_profile_str(self, doctor_profile):
        """Test doctor profile string representation."""
        expected = f"Dr. {doctor_profile.user.get_full_name()}"
        assert str(doctor_profile) == expected
