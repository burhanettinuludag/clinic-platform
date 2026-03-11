"""
Integration tests for migraine API endpoints.

Tests cover:
- MigraineAttackViewSet: CRUD, permissions, filtering, stats, chart, report, isolation
- MigraineTriggerViewSet: CRUD, permissions, queryset scoping, analysis
"""

import pytest
from datetime import timedelta, date
from django.utils import timezone
from rest_framework import status
from apps.migraine.models import MigraineAttack, MigraineTrigger


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

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


@pytest.fixture
def dietary_trigger(db):
    return MigraineTrigger.objects.create(
        name_tr='Cikolata', name_en='Chocolate',
        category='dietary', is_predefined=True,
    )


@pytest.fixture
def attack_payload():
    """Valid payload for creating an attack."""
    return {
        'start_datetime': timezone.now().isoformat(),
        'intensity': 7,
        'pain_location': 'bilateral',
        'has_aura': True,
        'has_nausea': True,
        'has_photophobia': True,
        'has_phonophobia': False,
        'has_vomiting': False,
        'medication_taken': 'Sumatriptan 50mg',
    }


@pytest.fixture
def five_attacks(patient_user):
    """Create 5 attacks spread over 15 days."""
    now = timezone.now()
    attacks = []
    for i in range(5):
        attack = MigraineAttack.objects.create(
            patient=patient_user,
            start_datetime=now - timedelta(days=i * 3),
            intensity=4 + (i % 4),  # 4, 5, 6, 7, 4
            pain_location=['left', 'right', 'bilateral', 'frontal', 'occipital'][i],
            has_aura=i % 2 == 0,
            duration_minutes=60 + i * 30,
        )
        attacks.append(attack)
    return attacks


# ---------------------------------------------------------------------------
# MigraineAttackViewSet — Authentication & Permissions
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestAttackPermissions:
    """Access control for migraine attack endpoints."""

    def test_anonymous_user_gets_401(self, api_client):
        response = api_client.get('/api/v1/migraine/attacks/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_doctor_gets_403(self, doctor_client):
        response = doctor_client.get('/api/v1/migraine/attacks/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_patient_gets_200(self, authenticated_client):
        response = authenticated_client.get('/api/v1/migraine/attacks/')
        assert response.status_code == status.HTTP_200_OK

    def test_admin_superuser_bypass(self, admin_client):
        """Superuser should pass IsPatient permission (superuser bypass)."""
        response = admin_client.get('/api/v1/migraine/attacks/')
        assert response.status_code == status.HTTP_200_OK


# ---------------------------------------------------------------------------
# MigraineAttackViewSet — CRUD
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestAttackCRUD:
    """Create, read, update, delete operations for attacks."""

    def test_list_attacks_paginated(self, authenticated_client, five_attacks):
        response = authenticated_client.get('/api/v1/migraine/attacks/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 5
        assert 'results' in response.data

    def test_list_uses_list_serializer_fields(self, authenticated_client, five_attacks):
        """List endpoint should use MigraineAttackListSerializer (trigger_count, not full triggers)."""
        response = authenticated_client.get('/api/v1/migraine/attacks/')
        first = response.data['results'][0]
        assert 'trigger_count' in first
        assert 'triggers_identified' not in first

    def test_create_attack_success(self, authenticated_client, attack_payload):
        response = authenticated_client.post(
            '/api/v1/migraine/attacks/', attack_payload, format='json',
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['intensity'] == 7
        assert response.data['has_aura'] is True
        assert response.data['medication_taken'] == 'Sumatriptan 50mg'

    def test_create_attack_with_triggers(self, authenticated_client, attack_payload, stress_trigger, sleep_trigger):
        attack_payload['trigger_ids'] = [str(stress_trigger.id), str(sleep_trigger.id)]
        response = authenticated_client.post(
            '/api/v1/migraine/attacks/', attack_payload, format='json',
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert len(response.data['triggers_identified']) == 2

    def test_create_attack_auto_assigns_patient(self, authenticated_client, patient_user, attack_payload):
        """perform_create should set patient=request.user."""
        response = authenticated_client.post(
            '/api/v1/migraine/attacks/', attack_payload, format='json',
        )
        attack = MigraineAttack.objects.get(id=response.data['id'])
        assert attack.patient == patient_user

    def test_retrieve_attack_detail(self, authenticated_client, five_attacks):
        attack = five_attacks[0]
        response = authenticated_client.get(f'/api/v1/migraine/attacks/{attack.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == str(attack.id)
        # Detail uses MigraineAttackSerializer with triggers_identified
        assert 'triggers_identified' in response.data

    def test_update_attack_intensity(self, authenticated_client, five_attacks):
        attack = five_attacks[0]
        response = authenticated_client.patch(
            f'/api/v1/migraine/attacks/{attack.id}/',
            {'intensity': 9},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['intensity'] == 9

    def test_update_attack_triggers(self, authenticated_client, five_attacks, stress_trigger):
        attack = five_attacks[0]
        response = authenticated_client.patch(
            f'/api/v1/migraine/attacks/{attack.id}/',
            {'trigger_ids': [str(stress_trigger.id)]},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['triggers_identified']) == 1

    def test_delete_attack(self, authenticated_client, five_attacks):
        attack = five_attacks[0]
        response = authenticated_client.delete(f'/api/v1/migraine/attacks/{attack.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not MigraineAttack.objects.filter(id=attack.id).exists()


# ---------------------------------------------------------------------------
# MigraineAttackViewSet — Validation
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestAttackValidation:
    """Serializer-level validation for attack data."""

    def test_intensity_zero_rejected(self, authenticated_client):
        data = {
            'start_datetime': timezone.now().isoformat(),
            'intensity': 0,
        }
        response = authenticated_client.post('/api/v1/migraine/attacks/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_intensity_eleven_rejected(self, authenticated_client):
        data = {
            'start_datetime': timezone.now().isoformat(),
            'intensity': 11,
        }
        response = authenticated_client.post('/api/v1/migraine/attacks/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_intensity_one_accepted(self, authenticated_client):
        data = {
            'start_datetime': timezone.now().isoformat(),
            'intensity': 1,
        }
        response = authenticated_client.post('/api/v1/migraine/attacks/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED

    def test_intensity_ten_accepted(self, authenticated_client):
        data = {
            'start_datetime': timezone.now().isoformat(),
            'intensity': 10,
        }
        response = authenticated_client.post('/api/v1/migraine/attacks/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED

    def test_intensity_negative_rejected(self, authenticated_client):
        data = {
            'start_datetime': timezone.now().isoformat(),
            'intensity': -1,
        }
        response = authenticated_client.post('/api/v1/migraine/attacks/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_missing_start_datetime_rejected(self, authenticated_client):
        data = {'intensity': 5}
        response = authenticated_client.post('/api/v1/migraine/attacks/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_missing_intensity_rejected(self, authenticated_client):
        data = {'start_datetime': timezone.now().isoformat()}
        response = authenticated_client.post('/api/v1/migraine/attacks/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_pain_location_rejected(self, authenticated_client):
        data = {
            'start_datetime': timezone.now().isoformat(),
            'intensity': 5,
            'pain_location': 'nonexistent_location',
        }
        response = authenticated_client.post('/api/v1/migraine/attacks/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ---------------------------------------------------------------------------
# MigraineAttackViewSet — Data Isolation
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestAttackIsolation:
    """Patient data isolation: each patient sees only their own attacks."""

    def test_patient_cannot_see_other_patients_attacks(
        self, api_client, user_factory, patient_user,
    ):
        """Patient A should not see Patient B's attacks."""
        patient_b = user_factory(email='other@test.com', role='patient')

        MigraineAttack.objects.create(
            patient=patient_user,
            start_datetime=timezone.now(),
            intensity=5,
        )
        MigraineAttack.objects.create(
            patient=patient_b,
            start_datetime=timezone.now(),
            intensity=8,
        )

        # Authenticate as patient_b
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(patient_b)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        response = api_client.get('/api/v1/migraine/attacks/')
        assert response.data['count'] == 1
        assert response.data['results'][0]['intensity'] == 8

    def test_patient_cannot_access_other_patients_attack_detail(
        self, api_client, user_factory, patient_user,
    ):
        """Patient B should get 404 for Patient A's attack (not in their queryset)."""
        patient_b = user_factory(email='other2@test.com', role='patient')

        attack_a = MigraineAttack.objects.create(
            patient=patient_user,
            start_datetime=timezone.now(),
            intensity=5,
        )

        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(patient_b)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        response = api_client.get(f'/api/v1/migraine/attacks/{attack_a.id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ---------------------------------------------------------------------------
# MigraineAttackViewSet — Filtering
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestAttackFiltering:
    """Date and field-based filtering."""

    def test_filter_by_date_range(self, authenticated_client, five_attacks):
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        response = authenticated_client.get(
            f'/api/v1/migraine/attacks/?start_date={week_ago}&end_date={today}'
        )
        assert response.status_code == status.HTTP_200_OK
        # Attacks within last 7 days: day 0, day 3, day 6 → at least 2-3
        assert response.data['count'] >= 2

    def test_filter_by_pain_location(self, authenticated_client, five_attacks):
        response = authenticated_client.get('/api/v1/migraine/attacks/?pain_location=left')
        assert response.status_code == status.HTTP_200_OK
        for result in response.data['results']:
            assert result['pain_location'] == 'left'

    def test_filter_by_has_aura(self, authenticated_client, five_attacks):
        response = authenticated_client.get('/api/v1/migraine/attacks/?has_aura=true')
        assert response.status_code == status.HTTP_200_OK
        for result in response.data['results']:
            assert result['has_aura'] is True

    def test_filter_by_start_date_only(self, authenticated_client, five_attacks):
        cutoff = (timezone.now() - timedelta(days=5)).date()
        response = authenticated_client.get(f'/api/v1/migraine/attacks/?start_date={cutoff}')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] >= 1


# ---------------------------------------------------------------------------
# MigraineAttackViewSet — Stats endpoint
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestAttackStats:
    """Tests for /attacks/stats/ custom action."""

    def test_stats_with_data(self, authenticated_client, five_attacks):
        response = authenticated_client.get('/api/v1/migraine/attacks/stats/')
        assert response.status_code == status.HTTP_200_OK
        data = response.data
        assert data['total_attacks'] == 5
        assert isinstance(data['avg_intensity'], float)
        assert isinstance(data['avg_duration'], float)
        assert 'attacks_this_month' in data
        assert 'attacks_last_month' in data
        assert 'most_common_triggers' in data
        assert 'most_common_location' in data
        assert 'aura_percentage' in data

    def test_stats_empty_patient(self, authenticated_client):
        """Stats for a patient with no attacks."""
        response = authenticated_client.get('/api/v1/migraine/attacks/stats/')
        assert response.status_code == status.HTTP_200_OK
        data = response.data
        assert data['total_attacks'] == 0
        assert data['avg_intensity'] == 0
        assert data['avg_duration'] == 0
        assert data['aura_percentage'] == 0
        assert data['most_common_location'] == ''

    def test_stats_trigger_ranking(
        self, authenticated_client, patient_user, stress_trigger, sleep_trigger,
    ):
        """most_common_triggers should be ordered by frequency."""
        now = timezone.now()
        for i in range(3):
            a = MigraineAttack.objects.create(
                patient=patient_user,
                start_datetime=now - timedelta(days=i),
                intensity=5,
            )
            a.triggers_identified.add(stress_trigger)

        a2 = MigraineAttack.objects.create(
            patient=patient_user,
            start_datetime=now - timedelta(days=10),
            intensity=4,
        )
        a2.triggers_identified.add(sleep_trigger)

        response = authenticated_client.get('/api/v1/migraine/attacks/stats/')
        triggers = response.data['most_common_triggers']
        assert len(triggers) == 2
        assert triggers[0]['name'] == 'Stres'  # 3 attacks
        assert triggers[0]['count'] == 3
        assert triggers[1]['name'] == 'Uykusuzluk'  # 1 attack

    def test_stats_aura_percentage_calculation(self, authenticated_client, patient_user):
        """Aura percentage = (aura_attacks / total) * 100."""
        now = timezone.now()
        for i in range(4):
            MigraineAttack.objects.create(
                patient=patient_user,
                start_datetime=now - timedelta(days=i),
                intensity=5,
                has_aura=(i < 1),  # 1 out of 4 = 25%
            )
        response = authenticated_client.get('/api/v1/migraine/attacks/stats/')
        assert response.data['aura_percentage'] == 25.0


# ---------------------------------------------------------------------------
# MigraineAttackViewSet — Chart endpoint
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestAttackChart:
    """Tests for /attacks/chart/ custom action."""

    def test_chart_returns_monthly_data(self, authenticated_client, five_attacks):
        response = authenticated_client.get('/api/v1/migraine/attacks/chart/?months=6')
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) > 0
        first = response.data[0]
        assert 'month' in first
        assert 'count' in first
        assert 'avg_intensity' in first

    def test_chart_default_months(self, authenticated_client, five_attacks):
        """Default should be 6 months."""
        response = authenticated_client.get('/api/v1/migraine/attacks/chart/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_chart_empty_patient(self, authenticated_client):
        response = authenticated_client.get('/api/v1/migraine/attacks/chart/?months=3')
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        # Months still present, but counts should be 0
        for entry in response.data:
            assert entry['count'] == 0
            assert entry['avg_intensity'] == 0


# ---------------------------------------------------------------------------
# MigraineAttackViewSet — Report endpoint
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestAttackReport:
    """Tests for /attacks/report/ PDF generation."""

    def test_report_returns_pdf(self, authenticated_client, five_attacks):
        response = authenticated_client.get('/api/v1/migraine/attacks/report/')
        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'application/pdf'
        assert 'Content-Disposition' in response
        assert 'migraine_report_' in response['Content-Disposition']

    def test_report_with_date_range(self, authenticated_client, five_attacks):
        today = timezone.now().date()
        start = today - timedelta(days=30)
        response = authenticated_client.get(
            f'/api/v1/migraine/attacks/report/?start_date={start}&end_date={today}'
        )
        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'application/pdf'

    def test_report_empty_patient(self, authenticated_client):
        """PDF should still generate even with no attacks."""
        response = authenticated_client.get('/api/v1/migraine/attacks/report/')
        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'application/pdf'


# ---------------------------------------------------------------------------
# MigraineTriggerViewSet — Permissions
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestTriggerPermissions:

    def test_anonymous_user_gets_401(self, api_client):
        response = api_client.get('/api/v1/migraine/triggers/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_doctor_gets_403(self, doctor_client):
        response = doctor_client.get('/api/v1/migraine/triggers/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_patient_gets_200(self, authenticated_client):
        response = authenticated_client.get('/api/v1/migraine/triggers/')
        assert response.status_code == status.HTTP_200_OK


# ---------------------------------------------------------------------------
# MigraineTriggerViewSet — CRUD & Queryset Scoping
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestTriggerCRUD:

    def test_list_shows_predefined_triggers(self, authenticated_client, stress_trigger):
        response = authenticated_client.get('/api/v1/migraine/triggers/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] >= 1

    def test_list_shows_own_custom_triggers(self, authenticated_client, patient_user):
        """Patient sees predefined + their own custom triggers."""
        MigraineTrigger.objects.create(
            name_tr='Benim tetikleyicim', name_en='My trigger',
            category='other', is_predefined=False, created_by=patient_user,
        )
        response = authenticated_client.get('/api/v1/migraine/triggers/')
        names = [t['name_en'] for t in response.data['results']]
        assert 'My trigger' in names

    def test_list_hides_other_patients_custom_triggers(
        self, authenticated_client, user_factory,
    ):
        """Patient should NOT see another patient's custom triggers."""
        other = user_factory(email='other3@test.com', role='patient')
        MigraineTrigger.objects.create(
            name_tr='Baskasinin', name_en='Other patient trigger',
            category='other', is_predefined=False, created_by=other,
        )
        response = authenticated_client.get('/api/v1/migraine/triggers/')
        names = [t['name_en'] for t in response.data['results']]
        assert 'Other patient trigger' not in names

    def test_create_custom_trigger(self, authenticated_client):
        data = {
            'name_tr': 'Parlak isik',
            'name_en': 'Bright light',
            'category': 'environmental',
        }
        response = authenticated_client.post(
            '/api/v1/migraine/triggers/', data, format='json',
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['is_predefined'] is False

    def test_create_trigger_auto_sets_created_by(self, authenticated_client, patient_user):
        data = {
            'name_tr': 'Yeni', 'name_en': 'New',
            'category': 'other',
        }
        response = authenticated_client.post(
            '/api/v1/migraine/triggers/', data, format='json',
        )
        trigger = MigraineTrigger.objects.get(id=response.data['id'])
        assert trigger.created_by == patient_user
        assert trigger.is_predefined is False

    def test_filter_by_category(self, authenticated_client, stress_trigger, sleep_trigger):
        response = authenticated_client.get('/api/v1/migraine/triggers/?category=emotional')
        assert response.status_code == status.HTTP_200_OK
        for t in response.data['results']:
            assert t['category'] == 'emotional'

    def test_filter_by_is_predefined(self, authenticated_client, stress_trigger, patient_user):
        MigraineTrigger.objects.create(
            name_tr='Ozel', name_en='Custom',
            category='other', is_predefined=False, created_by=patient_user,
        )
        response = authenticated_client.get('/api/v1/migraine/triggers/?is_predefined=true')
        for t in response.data['results']:
            assert t['is_predefined'] is True


# ---------------------------------------------------------------------------
# MigraineTriggerViewSet — Analysis endpoint
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestTriggerAnalysis:

    def test_analysis_with_data(
        self, authenticated_client, patient_user, stress_trigger, sleep_trigger,
    ):
        now = timezone.now()
        for i in range(3):
            a = MigraineAttack.objects.create(
                patient=patient_user,
                start_datetime=now - timedelta(days=i),
                intensity=5,
            )
            a.triggers_identified.add(stress_trigger)

        a2 = MigraineAttack.objects.create(
            patient=patient_user,
            start_datetime=now - timedelta(days=10),
            intensity=4,
        )
        a2.triggers_identified.add(sleep_trigger)

        response = authenticated_client.get('/api/v1/migraine/triggers/analysis/')
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) == 2
        # Should be ordered by attack_count descending
        assert response.data[0]['attack_count'] >= response.data[1]['attack_count']
        assert response.data[0]['name_en'] == 'Stress'

    def test_analysis_empty(self, authenticated_client):
        """No attacks → empty analysis."""
        response = authenticated_client.get('/api/v1/migraine/triggers/analysis/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data == []

    def test_analysis_only_own_attacks(
        self, authenticated_client, user_factory, patient_user, stress_trigger,
    ):
        """Analysis should only consider the requesting patient's attacks."""
        other = user_factory(email='other4@test.com', role='patient')
        now = timezone.now()

        # Other patient's attack
        a_other = MigraineAttack.objects.create(
            patient=other, start_datetime=now, intensity=8,
        )
        a_other.triggers_identified.add(stress_trigger)

        response = authenticated_client.get('/api/v1/migraine/triggers/analysis/')
        assert response.status_code == status.HTTP_200_OK
        # Current patient has no attacks, so analysis should be empty
        assert response.data == []
