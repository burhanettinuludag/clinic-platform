"""
Unit tests for migraine models.
"""

import pytest
from datetime import datetime, timedelta
from django.utils import timezone
from apps.migraine.models import MigraineAttack, MigraineTrigger


@pytest.mark.django_db
class TestMigraineTrigger:
    """Tests for MigraineTrigger model."""

    def test_create_predefined_trigger(self, db):
        """Test creating a predefined trigger."""
        trigger = MigraineTrigger.objects.create(
            name_tr='Stres',
            name_en='Stress',
            category=MigraineTrigger.TriggerCategory.EMOTIONAL,
            is_predefined=True,
        )
        assert trigger.name_en == 'Stress'
        assert trigger.category == 'emotional'
        assert trigger.is_predefined is True

    def test_create_custom_trigger(self, patient_user):
        """Test creating a custom trigger by patient."""
        trigger = MigraineTrigger.objects.create(
            name_tr='Ozel tetikleyici',
            name_en='Custom trigger',
            category=MigraineTrigger.TriggerCategory.OTHER,
            is_predefined=False,
            created_by=patient_user,
        )
        assert trigger.created_by == patient_user
        assert trigger.is_predefined is False

    def test_trigger_str_representation(self, db):
        """Test trigger string representation."""
        trigger = MigraineTrigger.objects.create(
            name_tr='Yorgunluk',
            name_en='Fatigue',
            category=MigraineTrigger.TriggerCategory.PHYSICAL,
        )
        assert str(trigger) == 'Fatigue'

    def test_trigger_categories(self, db):
        """Test all trigger category choices."""
        categories = [choice[0] for choice in MigraineTrigger.TriggerCategory.choices]
        expected = ['dietary', 'environmental', 'hormonal', 'emotional', 'physical', 'sleep', 'other']
        assert categories == expected


@pytest.mark.django_db
class TestMigraineAttack:
    """Tests for MigraineAttack model."""

    @pytest.fixture
    def sample_attack(self, patient_user):
        """Create a sample migraine attack."""
        return MigraineAttack.objects.create(
            patient=patient_user,
            start_datetime=timezone.now(),
            intensity=7,
            pain_location=MigraineAttack.PainLocation.LEFT,
            has_aura=True,
            has_nausea=True,
            has_photophobia=True,
        )

    def test_create_attack(self, sample_attack):
        """Test creating a migraine attack."""
        assert sample_attack.intensity == 7
        assert sample_attack.pain_location == 'left'
        assert sample_attack.has_aura is True
        assert sample_attack.has_nausea is True

    def test_attack_str_representation(self, sample_attack):
        """Test attack string representation."""
        expected = f"Attack on {sample_attack.start_datetime.date()} - Intensity: 7"
        assert str(sample_attack) == expected

    def test_attack_with_duration(self, patient_user):
        """Test attack with end time and duration."""
        start = timezone.now()
        end = start + timedelta(hours=4)
        attack = MigraineAttack.objects.create(
            patient=patient_user,
            start_datetime=start,
            end_datetime=end,
            duration_minutes=240,
            intensity=5,
        )
        assert attack.duration_minutes == 240
        assert attack.end_datetime is not None

    def test_attack_with_triggers(self, patient_user):
        """Test attack with associated triggers."""
        trigger1 = MigraineTrigger.objects.create(
            name_tr='Stres',
            name_en='Stress',
            category=MigraineTrigger.TriggerCategory.EMOTIONAL,
        )
        trigger2 = MigraineTrigger.objects.create(
            name_tr='Uykusuzluk',
            name_en='Lack of sleep',
            category=MigraineTrigger.TriggerCategory.SLEEP,
        )
        attack = MigraineAttack.objects.create(
            patient=patient_user,
            start_datetime=timezone.now(),
            intensity=6,
        )
        attack.triggers_identified.add(trigger1, trigger2)

        assert attack.triggers_identified.count() == 2
        assert trigger1 in attack.triggers_identified.all()

    def test_attack_pain_locations(self, db):
        """Test all pain location choices."""
        locations = [choice[0] for choice in MigraineAttack.PainLocation.choices]
        expected = ['left', 'right', 'bilateral', 'frontal', 'occipital', 'other']
        assert locations == expected

    def test_attack_ordering(self, patient_user):
        """Test attacks are ordered by start_datetime descending."""
        now = timezone.now()
        old_attack = MigraineAttack.objects.create(
            patient=patient_user,
            start_datetime=now - timedelta(days=7),
            intensity=5,
        )
        new_attack = MigraineAttack.objects.create(
            patient=patient_user,
            start_datetime=now,
            intensity=6,
        )

        attacks = list(MigraineAttack.objects.filter(patient=patient_user))
        assert attacks[0] == new_attack
        assert attacks[1] == old_attack
