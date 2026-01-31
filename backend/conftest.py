"""
Pytest configuration and fixtures for the clinic-platform backend.
"""

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.fixture
def api_client():
    """Return an unauthenticated API client."""
    return APIClient()


@pytest.fixture
def user_factory(db):
    """Factory for creating test users."""
    from apps.accounts.models import CustomUser

    def create_user(
        email='test@example.com',
        password='testpass123',
        role='patient',
        **kwargs
    ):
        defaults = {
            'first_name': 'Test',
            'last_name': 'User',
            'is_active': True,
        }
        defaults.update(kwargs)
        user = CustomUser.objects.create_user(
            email=email,
            password=password,
            role=role,
            **defaults
        )
        return user

    return create_user


@pytest.fixture
def patient_user(user_factory):
    """Create a patient user."""
    return user_factory(
        email='patient@example.com',
        role='patient',
        first_name='Test',
        last_name='Patient'
    )


@pytest.fixture
def doctor_user(user_factory):
    """Create a doctor user."""
    return user_factory(
        email='doctor@example.com',
        role='doctor',
        first_name='Test',
        last_name='Doctor'
    )


@pytest.fixture
def admin_user(user_factory):
    """Create an admin user."""
    return user_factory(
        email='admin@example.com',
        role='admin',
        first_name='Test',
        last_name='Admin',
        is_staff=True,
        is_superuser=True
    )


@pytest.fixture
def authenticated_client(api_client, patient_user):
    """Return an API client authenticated as a patient."""
    refresh = RefreshToken.for_user(patient_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def doctor_client(api_client, doctor_user):
    """Return an API client authenticated as a doctor."""
    refresh = RefreshToken.for_user(doctor_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """Return an API client authenticated as an admin."""
    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def patient_profile(db, patient_user):
    """Create a patient profile for the patient user."""
    from apps.accounts.models import PatientProfile

    profile, _ = PatientProfile.objects.get_or_create(
        user=patient_user,
        defaults={
            'gender': 'male',
            'emergency_contact_name': 'Emergency Contact',
            'emergency_contact_phone': '+901234567890',
        }
    )
    return profile


@pytest.fixture
def doctor_profile(db, doctor_user):
    """Create a doctor profile for the doctor user."""
    from apps.accounts.models import DoctorProfile

    profile, _ = DoctorProfile.objects.get_or_create(
        user=doctor_user,
        defaults={
            'specialty': 'Neurology',
            'license_number': 'DOC12345',
            'bio': 'Experienced neurologist',
            'is_accepting_patients': True,
        }
    )
    return profile


@pytest.fixture
def disease_module(db):
    """Create a disease module for testing."""
    from apps.patients.models import DiseaseModule

    module, _ = DiseaseModule.objects.get_or_create(
        slug='migraine',
        defaults={
            'name_tr': 'Migren',
            'name_en': 'Migraine',
            'description_tr': 'Migren hastaligi modulu',
            'description_en': 'Migraine disease module',
            'is_active': True,
        }
    )
    return module
