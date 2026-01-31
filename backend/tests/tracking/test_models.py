"""
Unit tests for tracking models.
"""

import pytest
from datetime import date, time
from django.utils import timezone
from apps.tracking.models import (
    SymptomDefinition, SymptomEntry, Medication, MedicationLog, ReminderConfig
)


@pytest.mark.django_db
class TestMedication:
    """Tests for Medication model."""

    def test_create_medication(self, patient_user):
        """Test creating a medication."""
        medication = Medication.objects.create(
            patient=patient_user,
            name='Sumatriptan',
            dosage='50mg',
            frequency='As needed',
            is_active=True,
        )
        assert medication.name == 'Sumatriptan'
        assert medication.dosage == '50mg'
        assert medication.is_active is True

    def test_medication_str_representation(self, patient_user):
        """Test medication string representation."""
        medication = Medication.objects.create(
            patient=patient_user,
            name='Topiramate',
            dosage='25mg',
        )
        assert str(medication) == 'Topiramate (25mg)'

    def test_medication_with_date_range(self, patient_user):
        """Test medication with start and end dates."""
        medication = Medication.objects.create(
            patient=patient_user,
            name='Propranolol',
            dosage='40mg',
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 30),
        )
        assert medication.start_date == date(2024, 1, 1)
        assert medication.end_date == date(2024, 6, 30)


@pytest.mark.django_db
class TestMedicationLog:
    """Tests for MedicationLog model."""

    @pytest.fixture
    def medication(self, patient_user):
        """Create a medication for testing."""
        return Medication.objects.create(
            patient=patient_user,
            name='Test Med',
            dosage='100mg',
        )

    def test_create_medication_log_taken(self, patient_user, medication):
        """Test creating a medication log for taken medication."""
        log = MedicationLog.objects.create(
            patient=patient_user,
            medication=medication,
            taken_at=timezone.now(),
            was_taken=True,
        )
        assert log.was_taken is True
        assert 'taken' in str(log)

    def test_create_medication_log_missed(self, patient_user, medication):
        """Test creating a medication log for missed medication."""
        log = MedicationLog.objects.create(
            patient=patient_user,
            medication=medication,
            taken_at=timezone.now(),
            was_taken=False,
        )
        assert log.was_taken is False
        assert 'missed' in str(log)


@pytest.mark.django_db
class TestSymptomDefinition:
    """Tests for SymptomDefinition model."""

    def test_create_symptom_definition(self, disease_module):
        """Test creating a symptom definition."""
        symptom = SymptomDefinition.objects.create(
            disease_module=disease_module,
            key='pain_level',
            label_tr='Agri Seviyesi',
            label_en='Pain Level',
            input_type=SymptomDefinition.InputType.SLIDER,
            config={'min': 0, 'max': 10},
        )
        assert symptom.key == 'pain_level'
        assert symptom.input_type == 'slider'

    def test_symptom_input_types(self, db):
        """Test all input type choices."""
        types = [choice[0] for choice in SymptomDefinition.InputType.choices]
        expected = ['slider', 'boolean', 'choice', 'text', 'number']
        assert types == expected


@pytest.mark.django_db
class TestSymptomEntry:
    """Tests for SymptomEntry model."""

    @pytest.fixture
    def symptom_definition(self, disease_module):
        """Create a symptom definition."""
        return SymptomDefinition.objects.create(
            disease_module=disease_module,
            key='headache_intensity',
            label_tr='Bas agrisi siddeti',
            label_en='Headache intensity',
            input_type='slider',
        )

    def test_create_symptom_entry(self, patient_user, symptom_definition):
        """Test creating a symptom entry."""
        entry = SymptomEntry.objects.create(
            patient=patient_user,
            symptom_definition=symptom_definition,
            recorded_date=date.today(),
            value=7,
        )
        assert entry.value == 7
        assert entry.recorded_date == date.today()

    def test_unique_entry_per_day(self, patient_user, symptom_definition):
        """Test that only one entry per symptom per day is allowed."""
        SymptomEntry.objects.create(
            patient=patient_user,
            symptom_definition=symptom_definition,
            recorded_date=date.today(),
            value=5,
        )
        with pytest.raises(Exception):  # IntegrityError
            SymptomEntry.objects.create(
                patient=patient_user,
                symptom_definition=symptom_definition,
                recorded_date=date.today(),
                value=6,
            )


@pytest.mark.django_db
class TestReminderConfig:
    """Tests for ReminderConfig model."""

    def test_create_reminder(self, patient_user):
        """Test creating a reminder."""
        reminder = ReminderConfig.objects.create(
            patient=patient_user,
            reminder_type=ReminderConfig.ReminderType.MEDICATION,
            title='Take morning medication',
            time_of_day=time(8, 0),
            days_of_week=[1, 2, 3, 4, 5],  # Weekdays
            is_enabled=True,
        )
        assert reminder.title == 'Take morning medication'
        assert reminder.reminder_type == 'medication'
        assert len(reminder.days_of_week) == 5

    def test_reminder_types(self, db):
        """Test all reminder type choices."""
        types = [choice[0] for choice in ReminderConfig.ReminderType.choices]
        expected = ['medication', 'exercise', 'sleep', 'diary', 'general']
        assert types == expected

    def test_reminder_linked_to_medication(self, patient_user):
        """Test reminder linked to medication."""
        medication = Medication.objects.create(
            patient=patient_user,
            name='Daily Med',
            dosage='50mg',
        )
        reminder = ReminderConfig.objects.create(
            patient=patient_user,
            reminder_type='medication',
            title='Take Daily Med',
            time_of_day=time(9, 0),
            days_of_week=[0, 1, 2, 3, 4, 5, 6],
            linked_medication=medication,
        )
        assert reminder.linked_medication == medication
