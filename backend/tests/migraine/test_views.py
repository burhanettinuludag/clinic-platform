"""
Integration tests for migraine API endpoints.
"""

import pytest
from datetime import timedelta
from django.utils import timezone
from rest_framework import status
from apps.migraine.models import MigraineAttack, MigraineTrigger


@pytest.mark.django_db
class TestMigraineAttackViewSet:
    """Tests for migraine attack endpoints."""

    @pytest.fixture
    def create_attacks(self, patient_user):
        """Create sample attacks for testing."""
        now = timezone.now()
        attacks = []
        for i in range(5):
            attack = MigraineAttack.objects.create(
                patient=patient_user,
                start_datetime=now - timedelta(days=i * 3),
                intensity=5 + i % 3,
                pain_location='left',
                has_aura=i % 2 == 0,
            )
            attacks.append(attack)
        return attacks

    def test_list_attacks(self, authenticated_client, create_attacks):
        """Test listing migraine attacks."""
        response = authenticated_client.get('/api/v1/migraine/attacks/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 5

    def test_create_attack(self, authenticated_client):
        """Test creating a new migraine attack."""
        data = {
            'start_datetime': timezone.now().isoformat(),
            'intensity': 7,
            'pain_location': 'bilateral',
            'has_aura': True,
            'has_nausea': True,
            'has_photophobia': True,
            'medication_taken': 'Ibuprofen 400mg',
        }
        response = authenticated_client.post('/api/v1/migraine/attacks/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['intensity'] == 7
        assert response.data['has_aura'] is True

    def test_create_attack_invalid_intensity(self, authenticated_client):
        """Test creating attack with invalid intensity fails."""
        data = {
            'start_datetime': timezone.now().isoformat(),
            'intensity': 15,  # Invalid: should be 1-10
        }
        response = authenticated_client.post('/api/v1/migraine/attacks/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_attack_stats(self, authenticated_client, create_attacks):
        """Test getting migraine statistics."""
        response = authenticated_client.get('/api/v1/migraine/attacks/stats/')
        assert response.status_code == status.HTTP_200_OK
        assert 'total_attacks' in response.data
        assert 'avg_intensity' in response.data
        assert 'attacks_this_month' in response.data
        assert response.data['total_attacks'] == 5

    def test_get_chart_data(self, authenticated_client, create_attacks):
        """Test getting chart data for attacks."""
        response = authenticated_client.get('/api/v1/migraine/attacks/chart/?months=3')
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        if len(response.data) > 0:
            assert 'month' in response.data[0]
            assert 'count' in response.data[0]
            assert 'avg_intensity' in response.data[0]

    def test_filter_attacks_by_date(self, authenticated_client, create_attacks):
        """Test filtering attacks by date range."""
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        response = authenticated_client.get(
            f'/api/v1/migraine/attacks/?start_date={week_ago}&end_date={today}'
        )
        assert response.status_code == status.HTTP_200_OK

    def test_doctor_cannot_access_patient_attacks(self, doctor_client):
        """Test doctor cannot access migraine attack endpoints."""
        response = doctor_client.get('/api/v1/migraine/attacks/')
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestMigraineTriggerViewSet:
    """Tests for migraine trigger endpoints."""

    @pytest.fixture
    def predefined_triggers(self, db):
        """Create predefined triggers."""
        triggers = [
            MigraineTrigger.objects.create(
                name_tr='Stres',
                name_en='Stress',
                category='emotional',
                is_predefined=True,
            ),
            MigraineTrigger.objects.create(
                name_tr='Uykusuzluk',
                name_en='Lack of sleep',
                category='sleep',
                is_predefined=True,
            ),
        ]
        return triggers

    def test_list_triggers(self, authenticated_client, predefined_triggers):
        """Test listing triggers."""
        response = authenticated_client.get('/api/v1/migraine/triggers/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] >= 2

    def test_create_custom_trigger(self, authenticated_client):
        """Test creating a custom trigger."""
        data = {
            'name_tr': 'Ozel tetikleyici',
            'name_en': 'Custom trigger',
            'category': 'other',
        }
        response = authenticated_client.post('/api/v1/migraine/triggers/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['is_predefined'] is False

    def test_trigger_analysis(self, authenticated_client, patient_user, predefined_triggers):
        """Test trigger analysis endpoint."""
        # Create attack with triggers
        attack = MigraineAttack.objects.create(
            patient=patient_user,
            start_datetime=timezone.now(),
            intensity=6,
        )
        attack.triggers_identified.add(predefined_triggers[0])

        response = authenticated_client.get('/api/v1/migraine/triggers/analysis/')
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        if len(response.data) > 0:
            assert 'attack_count' in response.data[0]

    def test_filter_triggers_by_category(self, authenticated_client, predefined_triggers):
        """Test filtering triggers by category."""
        response = authenticated_client.get('/api/v1/migraine/triggers/?category=emotional')
        assert response.status_code == status.HTTP_200_OK
