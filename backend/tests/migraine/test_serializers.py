"""
Unit tests for migraine serializers.

Tests cover:
- MigraineTriggerSerializer: bilingual name resolution, field presence
- MigraineAttackSerializer: intensity validation, trigger assignment, create/update
- MigraineAttackListSerializer: lightweight fields, trigger_count
- MigraineStatsSerializer: field presence
"""

import pytest
from datetime import timedelta
from django.utils import timezone
from django.test import RequestFactory
from rest_framework.request import Request
from apps.migraine.models import MigraineAttack, MigraineTrigger
from apps.migraine.serializers import (
    MigraineTriggerSerializer,
    MigraineAttackSerializer,
    MigraineAttackListSerializer,
    MigraineStatsSerializer,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def rf():
    """Django RequestFactory."""
    return RequestFactory()


@pytest.fixture
def stress_trigger(db):
    return MigraineTrigger.objects.create(
        name_tr='Stres', name_en='Stress',
        category='emotional', is_predefined=True,
    )


@pytest.fixture
def sleep_trigger(db):
    return MigraineTrigger.objects.create(
        name_tr='Uykusuzluk', name_en='Lack of sleep',
        category='sleep', is_predefined=True,
    )


def _make_drf_request(rf, lang='tr'):
    """Create a DRF Request with Accept-Language header."""
    django_request = rf.get('/', HTTP_ACCEPT_LANGUAGE=lang)
    return Request(django_request)


# ---------------------------------------------------------------------------
# MigraineTriggerSerializer
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestMigraineTriggerSerializer:

    def test_name_resolves_to_turkish_by_default(self, rf, stress_trigger):
        request = _make_drf_request(rf, 'tr')
        serializer = MigraineTriggerSerializer(stress_trigger, context={'request': request})
        assert serializer.data['name'] == 'Stres'

    def test_name_resolves_to_english(self, rf, stress_trigger):
        request = _make_drf_request(rf, 'en')
        serializer = MigraineTriggerSerializer(stress_trigger, context={'request': request})
        assert serializer.data['name'] == 'Stress'

    def test_name_fallback_to_turkish_for_unknown_lang(self, rf, stress_trigger):
        request = _make_drf_request(rf, 'de')
        serializer = MigraineTriggerSerializer(stress_trigger, context={'request': request})
        # getattr(obj, 'name_de') returns None → falls back to name_tr
        assert serializer.data['name'] == 'Stres'

    def test_name_without_request_context(self, stress_trigger):
        """No request context → default to Turkish."""
        serializer = MigraineTriggerSerializer(stress_trigger, context={})
        assert serializer.data['name'] == 'Stres'

    def test_serialized_fields(self, rf, stress_trigger):
        request = _make_drf_request(rf, 'tr')
        serializer = MigraineTriggerSerializer(stress_trigger, context={'request': request})
        expected_fields = {'id', 'name', 'name_tr', 'name_en', 'category', 'is_predefined', 'created_by'}
        assert set(serializer.data.keys()) == expected_fields

    def test_created_by_is_read_only(self, rf):
        """created_by should not be writable through serializer."""
        request = _make_drf_request(rf, 'tr')
        data = {
            'name_tr': 'Test', 'name_en': 'Test',
            'category': 'other', 'created_by': 'some-uuid',
        }
        serializer = MigraineTriggerSerializer(data=data, context={'request': request})
        assert serializer.is_valid()
        # created_by is read_only, so it should not be in validated_data
        assert 'created_by' not in serializer.validated_data


# ---------------------------------------------------------------------------
# MigraineAttackSerializer — Validation
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestMigraineAttackSerializerValidation:

    def test_intensity_zero_invalid(self):
        data = {
            'start_datetime': timezone.now().isoformat(),
            'intensity': 0,
        }
        serializer = MigraineAttackSerializer(data=data)
        assert not serializer.is_valid()
        assert 'intensity' in serializer.errors

    def test_intensity_one_valid(self):
        data = {
            'start_datetime': timezone.now().isoformat(),
            'intensity': 1,
        }
        serializer = MigraineAttackSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_intensity_ten_valid(self):
        data = {
            'start_datetime': timezone.now().isoformat(),
            'intensity': 10,
        }
        serializer = MigraineAttackSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_intensity_eleven_invalid(self):
        data = {
            'start_datetime': timezone.now().isoformat(),
            'intensity': 11,
        }
        serializer = MigraineAttackSerializer(data=data)
        assert not serializer.is_valid()
        assert 'intensity' in serializer.errors

    def test_intensity_negative_invalid(self):
        data = {
            'start_datetime': timezone.now().isoformat(),
            'intensity': -5,
        }
        serializer = MigraineAttackSerializer(data=data)
        assert not serializer.is_valid()


# ---------------------------------------------------------------------------
# MigraineAttackSerializer — Create & Update
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestMigraineAttackSerializerCRUD:

    def test_create_without_triggers(self, patient_user):
        data = {
            'start_datetime': timezone.now().isoformat(),
            'intensity': 6,
            'pain_location': 'frontal',
            'has_aura': False,
        }
        serializer = MigraineAttackSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        attack = serializer.save(patient=patient_user)
        assert attack.pk is not None
        assert attack.patient == patient_user
        assert attack.triggers_identified.count() == 0

    def test_create_with_triggers(self, patient_user, stress_trigger, sleep_trigger):
        data = {
            'start_datetime': timezone.now().isoformat(),
            'intensity': 8,
            'trigger_ids': [str(stress_trigger.id), str(sleep_trigger.id)],
        }
        serializer = MigraineAttackSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        attack = serializer.save(patient=patient_user)
        assert attack.triggers_identified.count() == 2

    def test_update_intensity(self, patient_user):
        attack = MigraineAttack.objects.create(
            patient=patient_user,
            start_datetime=timezone.now(),
            intensity=5,
        )
        serializer = MigraineAttackSerializer(
            attack, data={'intensity': 9}, partial=True,
        )
        assert serializer.is_valid()
        updated = serializer.save()
        assert updated.intensity == 9

    def test_update_triggers(self, patient_user, stress_trigger, sleep_trigger):
        attack = MigraineAttack.objects.create(
            patient=patient_user,
            start_datetime=timezone.now(),
            intensity=5,
        )
        attack.triggers_identified.add(stress_trigger)
        assert attack.triggers_identified.count() == 1

        serializer = MigraineAttackSerializer(
            attack,
            data={'trigger_ids': [str(sleep_trigger.id)]},
            partial=True,
        )
        assert serializer.is_valid()
        updated = serializer.save()
        assert updated.triggers_identified.count() == 1
        assert sleep_trigger in updated.triggers_identified.all()
        assert stress_trigger not in updated.triggers_identified.all()

    def test_update_without_triggers_key_preserves_existing(self, patient_user, stress_trigger):
        """If trigger_ids not sent in update, existing triggers should remain."""
        attack = MigraineAttack.objects.create(
            patient=patient_user,
            start_datetime=timezone.now(),
            intensity=5,
        )
        attack.triggers_identified.add(stress_trigger)

        serializer = MigraineAttackSerializer(
            attack, data={'intensity': 3}, partial=True,
        )
        assert serializer.is_valid()
        updated = serializer.save()
        assert updated.intensity == 3
        assert updated.triggers_identified.count() == 1  # preserved


# ---------------------------------------------------------------------------
# MigraineAttackListSerializer
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestMigraineAttackListSerializer:

    def test_fields_present(self, patient_user, stress_trigger):
        attack = MigraineAttack.objects.create(
            patient=patient_user,
            start_datetime=timezone.now(),
            intensity=6,
            pain_location='left',
            has_aura=True,
            duration_minutes=120,
            medication_taken='Ibuprofen',
        )
        attack.triggers_identified.add(stress_trigger)

        serializer = MigraineAttackListSerializer(attack)
        data = serializer.data
        expected_keys = {
            'id', 'start_datetime', 'duration_minutes',
            'intensity', 'pain_location', 'has_aura',
            'medication_taken', 'trigger_count', 'created_at',
        }
        assert set(data.keys()) == expected_keys

    def test_trigger_count(self, patient_user, stress_trigger, sleep_trigger):
        attack = MigraineAttack.objects.create(
            patient=patient_user,
            start_datetime=timezone.now(),
            intensity=5,
        )
        attack.triggers_identified.add(stress_trigger, sleep_trigger)
        serializer = MigraineAttackListSerializer(attack)
        assert serializer.data['trigger_count'] == 2

    def test_trigger_count_zero(self, patient_user):
        attack = MigraineAttack.objects.create(
            patient=patient_user,
            start_datetime=timezone.now(),
            intensity=5,
        )
        serializer = MigraineAttackListSerializer(attack)
        assert serializer.data['trigger_count'] == 0

    def test_does_not_include_full_triggers(self, patient_user):
        """List serializer should NOT have triggers_identified (only trigger_count)."""
        attack = MigraineAttack.objects.create(
            patient=patient_user,
            start_datetime=timezone.now(),
            intensity=5,
        )
        serializer = MigraineAttackListSerializer(attack)
        assert 'triggers_identified' not in serializer.data
        assert 'trigger_ids' not in serializer.data


# ---------------------------------------------------------------------------
# MigraineStatsSerializer
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestMigraineStatsSerializer:

    def test_stats_serializer_fields(self):
        data = {
            'total_attacks': 10,
            'avg_intensity': 6.5,
            'avg_duration': 180.0,
            'attacks_this_month': 3,
            'attacks_last_month': 4,
            'most_common_triggers': [{'name': 'Stres', 'count': 5}],
            'most_common_location': 'bilateral',
            'aura_percentage': 30.0,
        }
        serializer = MigraineStatsSerializer(data)
        assert serializer.data['total_attacks'] == 10
        assert serializer.data['avg_intensity'] == 6.5
        assert serializer.data['aura_percentage'] == 30.0

    def test_stats_serializer_empty_data(self):
        data = {
            'total_attacks': 0,
            'avg_intensity': 0.0,
            'avg_duration': 0.0,
            'attacks_this_month': 0,
            'attacks_last_month': 0,
            'most_common_triggers': [],
            'most_common_location': '',
            'aura_percentage': 0.0,
        }
        serializer = MigraineStatsSerializer(data)
        assert serializer.data['total_attacks'] == 0
        assert serializer.data['most_common_triggers'] == []
