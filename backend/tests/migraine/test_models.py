"""
Unit tests for migraine models.

Tests cover:
- MigraineTrigger: creation, categories, ordering, user-association
- MigraineAttack: creation, field validation, relationships, ordering, cascading
"""

import pytest
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from apps.migraine.models import MigraineAttack, MigraineTrigger


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def stress_trigger(db):
    """Predefined emotional trigger."""
    return MigraineTrigger.objects.create(
        name_tr='Stres',
        name_en='Stress',
        category=MigraineTrigger.TriggerCategory.EMOTIONAL,
        is_predefined=True,
    )


@pytest.fixture
def sleep_trigger(db):
    """Predefined sleep trigger."""
    return MigraineTrigger.objects.create(
        name_tr='Uykusuzluk',
        name_en='Lack of sleep',
        category=MigraineTrigger.TriggerCategory.SLEEP,
        is_predefined=True,
    )


@pytest.fixture
def sample_attack(patient_user):
    """Standard migraine attack for reuse."""
    return MigraineAttack.objects.create(
        patient=patient_user,
        start_datetime=timezone.now(),
        intensity=7,
        pain_location=MigraineAttack.PainLocation.LEFT,
        has_aura=True,
        has_nausea=True,
        has_photophobia=True,
    )


# ---------------------------------------------------------------------------
# MigraineTrigger tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestMigraineTrigger:
    """Tests for MigraineTrigger model."""

    def test_create_predefined_trigger(self, stress_trigger):
        assert stress_trigger.name_en == 'Stress'
        assert stress_trigger.category == 'emotional'
        assert stress_trigger.is_predefined is True
        assert stress_trigger.created_by is None

    def test_create_custom_trigger(self, patient_user):
        trigger = MigraineTrigger.objects.create(
            name_tr='Cikolata',
            name_en='Chocolate',
            category=MigraineTrigger.TriggerCategory.DIETARY,
            is_predefined=False,
            created_by=patient_user,
        )
        assert trigger.created_by == patient_user
        assert trigger.is_predefined is False

    def test_str_representation(self, stress_trigger):
        assert str(stress_trigger) == 'Stress'

    def test_all_trigger_categories_exist(self):
        categories = [c[0] for c in MigraineTrigger.TriggerCategory.choices]
        expected = [
            'dietary', 'environmental', 'hormonal',
            'emotional', 'physical', 'sleep', 'other',
        ]
        assert categories == expected

    def test_ordering_by_category_then_name(self, db):
        """Triggers should be ordered by category, then name_en (Meta.ordering)."""
        t_sleep = MigraineTrigger.objects.create(
            name_tr='Jet lag', name_en='Jet lag',
            category=MigraineTrigger.TriggerCategory.SLEEP,
        )
        t_diet = MigraineTrigger.objects.create(
            name_tr='Alkol', name_en='Alcohol',
            category=MigraineTrigger.TriggerCategory.DIETARY,
        )
        triggers = list(MigraineTrigger.objects.all())
        # 'dietary' < 'sleep' alphabetically → t_diet first
        assert triggers[0] == t_diet
        assert triggers[1] == t_sleep

    def test_created_by_set_null_on_user_delete(self, patient_user):
        """When user is deleted, custom trigger should remain with created_by=NULL."""
        trigger = MigraineTrigger.objects.create(
            name_tr='Ozel', name_en='Custom',
            category=MigraineTrigger.TriggerCategory.OTHER,
            is_predefined=False,
            created_by=patient_user,
        )
        trigger_id = trigger.id
        patient_user.delete()
        trigger.refresh_from_db()
        assert trigger.created_by is None

    def test_trigger_has_uuid_primary_key(self, stress_trigger):
        """TimeStampedModel provides UUID pk."""
        assert stress_trigger.pk is not None
        assert len(str(stress_trigger.pk)) == 36  # UUID format

    def test_trigger_timestamps(self, stress_trigger):
        """created_at and updated_at should be auto-populated."""
        assert stress_trigger.created_at is not None
        assert stress_trigger.updated_at is not None
        assert stress_trigger.created_at <= stress_trigger.updated_at


# ---------------------------------------------------------------------------
# MigraineAttack tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestMigraineAttack:
    """Tests for MigraineAttack model."""

    def test_create_minimal_attack(self, patient_user):
        """Attack with only required fields."""
        attack = MigraineAttack.objects.create(
            patient=patient_user,
            start_datetime=timezone.now(),
            intensity=1,
        )
        assert attack.pk is not None
        assert attack.pain_location == ''
        assert attack.has_aura is False
        assert attack.end_datetime is None
        assert attack.duration_minutes is None
        assert attack.medication_taken == ''
        assert attack.notes == ''

    def test_create_full_attack(self, patient_user, stress_trigger, sleep_trigger):
        """Attack with all fields populated."""
        start = timezone.now()
        end = start + timedelta(hours=6)
        attack = MigraineAttack.objects.create(
            patient=patient_user,
            start_datetime=start,
            end_datetime=end,
            duration_minutes=360,
            intensity=9,
            pain_location=MigraineAttack.PainLocation.BILATERAL,
            has_aura=True,
            has_nausea=True,
            has_vomiting=True,
            has_photophobia=True,
            has_phonophobia=True,
            medication_taken='Sumatriptan 50mg',
            medication_effective=True,
            notes='Preceded by visual aura for 20 min',
        )
        attack.triggers_identified.set([stress_trigger, sleep_trigger])

        assert attack.intensity == 9
        assert attack.duration_minutes == 360
        assert attack.has_phonophobia is True
        assert attack.medication_effective is True
        assert attack.triggers_identified.count() == 2

    def test_str_representation(self, sample_attack):
        expected = f"Attack on {sample_attack.start_datetime.date()} - Intensity: 7"
        assert str(sample_attack) == expected

    def test_all_pain_locations(self):
        locations = [loc[0] for loc in MigraineAttack.PainLocation.choices]
        expected = ['left', 'right', 'bilateral', 'frontal', 'occipital', 'other']
        assert locations == expected

    def test_ordering_descending_by_start(self, patient_user):
        """Attacks should be ordered newest-first."""
        now = timezone.now()
        old = MigraineAttack.objects.create(
            patient=patient_user,
            start_datetime=now - timedelta(days=7),
            intensity=4,
        )
        new = MigraineAttack.objects.create(
            patient=patient_user,
            start_datetime=now,
            intensity=8,
        )
        attacks = list(MigraineAttack.objects.filter(patient=patient_user))
        assert attacks[0] == new
        assert attacks[1] == old

    def test_attack_with_duration_and_end_datetime(self, patient_user):
        start = timezone.now()
        end = start + timedelta(hours=4, minutes=30)
        attack = MigraineAttack.objects.create(
            patient=patient_user,
            start_datetime=start,
            end_datetime=end,
            duration_minutes=270,
            intensity=5,
        )
        assert attack.duration_minutes == 270
        assert attack.end_datetime == end

    def test_trigger_many_to_many_add_remove(self, sample_attack, stress_trigger, sleep_trigger):
        """Test adding and removing triggers from attack."""
        sample_attack.triggers_identified.add(stress_trigger, sleep_trigger)
        assert sample_attack.triggers_identified.count() == 2

        sample_attack.triggers_identified.remove(stress_trigger)
        assert sample_attack.triggers_identified.count() == 1
        assert sleep_trigger in sample_attack.triggers_identified.all()

    def test_trigger_clear(self, sample_attack, stress_trigger):
        sample_attack.triggers_identified.add(stress_trigger)
        sample_attack.triggers_identified.clear()
        assert sample_attack.triggers_identified.count() == 0

    def test_cascade_delete_patient_removes_attacks(self, patient_user, sample_attack):
        """Deleting patient should cascade-delete all their attacks."""
        attack_id = sample_attack.id
        patient_user.delete()
        assert not MigraineAttack.objects.filter(id=attack_id).exists()

    def test_reverse_relation_from_trigger(self, patient_user, stress_trigger):
        """Trigger.attacks reverse relation should work."""
        attack = MigraineAttack.objects.create(
            patient=patient_user,
            start_datetime=timezone.now(),
            intensity=6,
        )
        attack.triggers_identified.add(stress_trigger)
        assert stress_trigger.attacks.count() == 1
        assert stress_trigger.attacks.first() == attack

    def test_patient_reverse_relation(self, patient_user, sample_attack):
        """patient.migraine_attacks reverse relation should work."""
        assert patient_user.migraine_attacks.count() == 1
        assert patient_user.migraine_attacks.first() == sample_attack

    def test_medication_effective_nullable(self, patient_user):
        """medication_effective can be True, False, or None (not recorded)."""
        attack = MigraineAttack.objects.create(
            patient=patient_user,
            start_datetime=timezone.now(),
            intensity=5,
            medication_taken='Paracetamol 500mg',
            medication_effective=None,
        )
        assert attack.medication_effective is None

    def test_intensity_boundary_min(self, patient_user):
        """Minimum valid intensity is 1 at model level (PositiveSmallIntegerField allows 0+)."""
        # Model allows 0 at DB level; validation is in serializer
        attack = MigraineAttack.objects.create(
            patient=patient_user,
            start_datetime=timezone.now(),
            intensity=1,
        )
        assert attack.intensity == 1

    def test_intensity_boundary_max(self, patient_user):
        """Maximum valid intensity is 10 (enforced by serializer, not model)."""
        attack = MigraineAttack.objects.create(
            patient=patient_user,
            start_datetime=timezone.now(),
            intensity=10,
        )
        assert attack.intensity == 10

    def test_multiple_patients_isolated(self, user_factory):
        """Each patient should only see their own attacks."""
        p1 = user_factory(email='p1@test.com', role='patient')
        p2 = user_factory(email='p2@test.com', role='patient')

        MigraineAttack.objects.create(
            patient=p1, start_datetime=timezone.now(), intensity=3,
        )
        MigraineAttack.objects.create(
            patient=p2, start_datetime=timezone.now(), intensity=8,
        )

        assert MigraineAttack.objects.filter(patient=p1).count() == 1
        assert MigraineAttack.objects.filter(patient=p2).count() == 1
        assert MigraineAttack.objects.filter(patient=p1).first().intensity == 3

    def test_index_exists_on_patient_start_datetime(self):
        """Composite index on (patient, -start_datetime) should exist."""
        index_fields = [
            idx.fields for idx in MigraineAttack._meta.indexes
        ]
        assert ['patient', '-start_datetime'] in index_fields
