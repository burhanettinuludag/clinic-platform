"""
Integration tests for tracking API endpoints.
"""

import pytest
from datetime import date, time, timedelta
from django.utils import timezone
from rest_framework import status
from apps.tracking.models import (
    SymptomDefinition,
    SymptomEntry,
    Medication,
    MedicationLog,
    ReminderConfig,
)
from apps.patients.models import PatientModule


@pytest.mark.django_db
class TestSymptomDefinitionViewSet:
    """Tests for symptom definition endpoints."""

    @pytest.fixture
    def enrolled_patient(self, patient_user, disease_module):
        """Create enrolled patient."""
        PatientModule.objects.create(
            patient=patient_user,
            disease_module=disease_module,
            is_active=True,
        )
        return patient_user

    @pytest.fixture
    def symptom_definitions(self, disease_module):
        """Create symptom definitions."""
        definitions = [
            SymptomDefinition.objects.create(
                disease_module=disease_module,
                key='pain_level',
                label_tr='Agri Seviyesi',
                label_en='Pain Level',
                input_type='slider',
                is_active=True,
            ),
            SymptomDefinition.objects.create(
                disease_module=disease_module,
                key='nausea',
                label_tr='Bulanti',
                label_en='Nausea',
                input_type='boolean',
                is_active=True,
            ),
        ]
        return definitions

    def test_list_symptom_definitions(self, authenticated_client, enrolled_patient, symptom_definitions):
        """Test listing symptom definitions for enrolled modules."""
        response = authenticated_client.get('/api/v1/tracking/symptoms/definitions/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2

    def test_filter_by_input_type(self, authenticated_client, enrolled_patient, symptom_definitions):
        """Test filtering definitions by input type."""
        response = authenticated_client.get('/api/v1/tracking/symptoms/definitions/?input_type=slider')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['key'] == 'pain_level'

    def test_unenrolled_patient_sees_nothing(self, authenticated_client, symptom_definitions):
        """Test unenrolled patient doesn't see definitions."""
        response = authenticated_client.get('/api/v1/tracking/symptoms/definitions/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 0


@pytest.mark.django_db
class TestSymptomEntryViewSet:
    """Tests for symptom entry endpoints."""

    @pytest.fixture
    def enrolled_patient(self, patient_user, disease_module):
        """Create enrolled patient."""
        PatientModule.objects.create(
            patient=patient_user,
            disease_module=disease_module,
            is_active=True,
        )
        return patient_user

    @pytest.fixture
    def symptom_definition(self, disease_module):
        """Create a symptom definition."""
        return SymptomDefinition.objects.create(
            disease_module=disease_module,
            key='pain_level',
            label_tr='Agri Seviyesi',
            label_en='Pain Level',
            input_type='slider',
            is_active=True,
        )

    def test_list_symptom_entries(self, authenticated_client, enrolled_patient, symptom_definition):
        """Test listing symptom entries."""
        SymptomEntry.objects.create(
            patient=enrolled_patient,
            symptom_definition=symptom_definition,
            recorded_date=date.today(),
            value=7,
        )
        response = authenticated_client.get('/api/v1/tracking/symptoms/entries/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

    def test_create_symptom_entry(self, authenticated_client, enrolled_patient, symptom_definition):
        """Test creating a symptom entry."""
        data = {
            'symptom_definition': symptom_definition.id,
            'recorded_date': date.today().isoformat(),
            'value': 6,
        }
        response = authenticated_client.post('/api/v1/tracking/symptoms/entries/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['value'] == 6

    def test_get_today_entries(self, authenticated_client, enrolled_patient, symptom_definition):
        """Test getting today's entries."""
        SymptomEntry.objects.create(
            patient=enrolled_patient,
            symptom_definition=symptom_definition,
            recorded_date=date.today(),
            value=5,
        )
        SymptomEntry.objects.create(
            patient=enrolled_patient,
            symptom_definition=symptom_definition,
            recorded_date=date.today() - timedelta(days=1),
            value=4,
        )
        response = authenticated_client.get('/api/v1/tracking/symptoms/entries/today/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['value'] == 5

    def test_get_chart_data(self, authenticated_client, enrolled_patient, symptom_definition):
        """Test getting chart data."""
        for i in range(7):
            SymptomEntry.objects.create(
                patient=enrolled_patient,
                symptom_definition=symptom_definition,
                recorded_date=date.today() - timedelta(days=i),
                value=5 + i % 3,
            )
        response = authenticated_client.get('/api/v1/tracking/symptoms/entries/chart/?days=7')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 7


@pytest.mark.django_db
class TestMedicationViewSet:
    """Tests for medication endpoints."""

    def test_list_medications(self, authenticated_client, patient_user):
        """Test listing medications."""
        Medication.objects.create(
            patient=patient_user,
            name='Sumatriptan',
            dosage='50mg',
            is_active=True,
        )
        response = authenticated_client.get('/api/v1/tracking/medications/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

    def test_create_medication(self, authenticated_client):
        """Test creating a medication."""
        data = {
            'name': 'Ibuprofen',
            'dosage': '400mg',
            'frequency': 'As needed',
            'is_active': True,
        }
        response = authenticated_client.post('/api/v1/tracking/medications/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Ibuprofen'

    def test_update_medication(self, authenticated_client, patient_user):
        """Test updating a medication."""
        medication = Medication.objects.create(
            patient=patient_user,
            name='Test Med',
            dosage='50mg',
        )
        response = authenticated_client.patch(
            f'/api/v1/tracking/medications/{medication.id}/',
            {'dosage': '100mg'}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['dosage'] == '100mg'

    def test_get_active_medications(self, authenticated_client, patient_user):
        """Test getting active medications."""
        Medication.objects.create(
            patient=patient_user,
            name='Active Med',
            dosage='50mg',
            is_active=True,
        )
        Medication.objects.create(
            patient=patient_user,
            name='Inactive Med',
            dosage='25mg',
            is_active=False,
        )
        response = authenticated_client.get('/api/v1/tracking/medications/active/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['name'] == 'Active Med'

    def test_delete_medication(self, authenticated_client, patient_user):
        """Test deleting a medication."""
        medication = Medication.objects.create(
            patient=patient_user,
            name='To Delete',
            dosage='50mg',
        )
        response = authenticated_client.delete(f'/api/v1/tracking/medications/{medication.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Medication.objects.filter(id=medication.id).count() == 0


@pytest.mark.django_db
class TestMedicationLogViewSet:
    """Tests for medication log endpoints."""

    @pytest.fixture
    def medication(self, patient_user):
        """Create a medication."""
        return Medication.objects.create(
            patient=patient_user,
            name='Test Med',
            dosage='50mg',
        )

    def test_list_medication_logs(self, authenticated_client, patient_user, medication):
        """Test listing medication logs."""
        MedicationLog.objects.create(
            patient=patient_user,
            medication=medication,
            taken_at=timezone.now(),
            was_taken=True,
        )
        response = authenticated_client.get('/api/v1/tracking/medications/logs/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

    def test_create_medication_log(self, authenticated_client, medication):
        """Test creating a medication log."""
        data = {
            'medication': medication.id,
            'taken_at': timezone.now().isoformat(),
            'was_taken': True,
        }
        response = authenticated_client.post('/api/v1/tracking/medications/logs/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['was_taken'] is True

    def test_get_today_logs(self, authenticated_client, patient_user, medication):
        """Test getting today's medication logs."""
        MedicationLog.objects.create(
            patient=patient_user,
            medication=medication,
            taken_at=timezone.now(),
            was_taken=True,
        )
        response = authenticated_client.get('/api/v1/tracking/medications/logs/today/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_get_adherence_rate(self, authenticated_client, patient_user, medication):
        """Test getting medication adherence rate."""
        # Create 8 taken, 2 missed logs
        for i in range(8):
            MedicationLog.objects.create(
                patient=patient_user,
                medication=medication,
                taken_at=timezone.now() - timedelta(days=i),
                was_taken=True,
            )
        for i in range(2):
            MedicationLog.objects.create(
                patient=patient_user,
                medication=medication,
                taken_at=timezone.now() - timedelta(days=10 + i),
                was_taken=False,
            )
        response = authenticated_client.get('/api/v1/tracking/medications/logs/adherence/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_logs'] == 10
        assert response.data['taken'] == 8
        assert response.data['missed'] == 2
        assert response.data['adherence_rate'] == 80.0


@pytest.mark.django_db
class TestReminderConfigViewSet:
    """Tests for reminder configuration endpoints."""

    def test_list_reminders(self, authenticated_client, patient_user):
        """Test listing reminders."""
        ReminderConfig.objects.create(
            patient=patient_user,
            reminder_type='medication',
            title='Morning Meds',
            time_of_day=time(8, 0),
            days_of_week=[1, 2, 3, 4, 5],
            is_enabled=True,
        )
        response = authenticated_client.get('/api/v1/tracking/reminders/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

    def test_create_reminder(self, authenticated_client):
        """Test creating a reminder."""
        data = {
            'reminder_type': 'medication',
            'title': 'Evening Meds',
            'time_of_day': '20:00:00',
            'days_of_week': [0, 1, 2, 3, 4, 5, 6],
            'is_enabled': True,
        }
        response = authenticated_client.post('/api/v1/tracking/reminders/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'Evening Meds'

    def test_update_reminder(self, authenticated_client, patient_user):
        """Test updating a reminder."""
        reminder = ReminderConfig.objects.create(
            patient=patient_user,
            reminder_type='medication',
            title='Test Reminder',
            time_of_day=time(8, 0),
            days_of_week=[1, 2, 3, 4, 5],
        )
        response = authenticated_client.patch(
            f'/api/v1/tracking/reminders/{reminder.id}/',
            {'is_enabled': False}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_enabled'] is False

    def test_delete_reminder(self, authenticated_client, patient_user):
        """Test deleting a reminder."""
        reminder = ReminderConfig.objects.create(
            patient=patient_user,
            reminder_type='exercise',
            title='To Delete',
            time_of_day=time(7, 0),
            days_of_week=[1, 2, 3, 4, 5],
        )
        response = authenticated_client.delete(f'/api/v1/tracking/reminders/{reminder.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestTrackingPermissions:
    """Tests for tracking endpoint permissions."""

    def test_unauthenticated_cannot_access_medications(self, api_client):
        """Test unauthenticated users cannot access medications."""
        response = api_client.get('/api/v1/tracking/medications/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_doctor_cannot_access_patient_medications(self, doctor_client):
        """Test doctor cannot access medication endpoints."""
        response = doctor_client.get('/api/v1/tracking/medications/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_doctor_cannot_create_reminders(self, doctor_client):
        """Test doctor cannot create reminders."""
        data = {
            'reminder_type': 'medication',
            'title': 'Test',
            'time_of_day': '08:00:00',
            'days_of_week': [1, 2, 3],
        }
        response = doctor_client.post('/api/v1/tracking/reminders/', data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
