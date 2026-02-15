"""
Integration tests for Marketing Campaign API endpoints.
Tests authentication, authorization, CRUD operations, approve, and regenerate.
"""

import pytest
from datetime import date
from unittest.mock import patch, MagicMock
from rest_framework import status
from apps.common.models import MarketingCampaign


# ============================
# FIXTURES
# ============================

@pytest.fixture
def campaign(db, doctor_user):
    """Create a test campaign in 'review' status."""
    return MarketingCampaign.objects.create(
        title='Test Kampanya',
        theme='Migren Farkindalik Haftasi',
        week_start=date(2026, 3, 2),
        status='review',
        platforms=['instagram', 'linkedin', 'twitter'],
        language='tr',
        tone='educational',
        target_audience='patients',
        content_output={'instagram_posts': [{'content': 'Test post'}]},
        visual_briefs={'briefs': [{'layout': 'single'}]},
        schedule={'entries': [{'day': 'Monday', 'time': '09:00'}]},
        created_by=doctor_user,
        total_tokens=1500,
    )


@pytest.fixture
def generating_campaign(db, doctor_user):
    """Create a campaign in 'generating' status."""
    return MarketingCampaign.objects.create(
        title='Generating Kampanya',
        theme='Wellness Tema',
        week_start=date(2026, 3, 9),
        status='generating',
        created_by=doctor_user,
    )


@pytest.fixture
def approved_campaign(db, doctor_user):
    """Create a campaign in 'approved' status."""
    return MarketingCampaign.objects.create(
        title='Approved Kampanya',
        theme='Epilepsi Tema',
        week_start=date(2026, 3, 16),
        status='approved',
        created_by=doctor_user,
    )


# ============================
# AUTH & PERMISSION TESTS
# ============================

@pytest.mark.django_db
class TestMarketingAuth:
    """Tests for authentication and permission on marketing endpoints."""

    def test_unauthenticated_list_returns_401(self, api_client):
        response = api_client.get('/api/v1/doctor/marketing/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_patient_cannot_access(self, authenticated_client):
        response = authenticated_client.get('/api/v1/doctor/marketing/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_doctor_can_access(self, doctor_client, campaign):
        response = doctor_client.get('/api/v1/doctor/marketing/')
        assert response.status_code == status.HTTP_200_OK

    def test_admin_cannot_access_doctor_endpoint(self, admin_client, campaign):
        """IsDoctor permission only allows role=doctor, not admin."""
        response = admin_client.get('/api/v1/doctor/marketing/')
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ============================
# LIST TESTS
# ============================

@pytest.mark.django_db
class TestMarketingList:
    """Tests for campaign list endpoint."""

    def test_list_returns_campaigns(self, doctor_client, campaign):
        response = doctor_client.get('/api/v1/doctor/marketing/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['title'] == 'Test Kampanya'

    def test_list_includes_status_display(self, doctor_client, campaign):
        response = doctor_client.get('/api/v1/doctor/marketing/')
        assert response.status_code == status.HTTP_200_OK
        assert 'status_display' in response.data['results'][0]

    def test_list_includes_platforms(self, doctor_client, campaign):
        response = doctor_client.get('/api/v1/doctor/marketing/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'][0]['platforms'] == ['instagram', 'linkedin', 'twitter']

    def test_empty_list(self, doctor_client):
        response = doctor_client.get('/api/v1/doctor/marketing/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0
        assert response.data['results'] == []

    def test_list_ordered_by_week_start_desc(self, doctor_client, campaign, approved_campaign):
        response = doctor_client.get('/api/v1/doctor/marketing/')
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        # approved_campaign has week_start 2026-03-16, campaign has 2026-03-02
        assert results[0]['week_start'] == '2026-03-16'
        assert results[1]['week_start'] == '2026-03-02'


# ============================
# CREATE TESTS
# ============================

@pytest.mark.django_db
class TestMarketingCreate:
    """Tests for campaign creation endpoint."""

    @patch('apps.doctor_panel.tasks.run_marketing_pipeline')
    def test_create_campaign(self, mock_pipeline, doctor_client):
        mock_pipeline.delay = MagicMock()
        response = doctor_client.post(
            '/api/v1/doctor/marketing/',
            {
                'theme': 'Migren Farkindalik Haftasi',
                'week_start': '2026-03-02',
                'platforms': ['instagram', 'linkedin'],
                'language': 'tr',
                'tone': 'educational',
                'target_audience': 'patients',
            },
            format='json',
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert MarketingCampaign.objects.count() == 1
        campaign = MarketingCampaign.objects.first()
        assert campaign.title == 'Migren Farkindalik Haftasi'
        assert campaign.status == 'generating'

    @patch('apps.doctor_panel.tasks.run_marketing_pipeline')
    def test_create_sets_created_by(self, mock_pipeline, doctor_client, doctor_user):
        mock_pipeline.delay = MagicMock()
        response = doctor_client.post(
            '/api/v1/doctor/marketing/',
            {'theme': 'Test Tema Uzun', 'week_start': '2026-03-02'},
            format='json',
        )
        assert response.status_code == status.HTTP_201_CREATED
        campaign = MarketingCampaign.objects.first()
        assert campaign.created_by == doctor_user

    def test_create_theme_too_short(self, doctor_client):
        response = doctor_client.post(
            '/api/v1/doctor/marketing/',
            {'theme': 'AB', 'week_start': '2026-03-02'},
            format='json',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_missing_theme(self, doctor_client):
        response = doctor_client.post(
            '/api/v1/doctor/marketing/',
            {'week_start': '2026-03-02'},
            format='json',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_missing_week_start(self, doctor_client):
        response = doctor_client.post(
            '/api/v1/doctor/marketing/',
            {'theme': 'Valid Theme Here'},
            format='json',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_patient_cannot_create(self, authenticated_client):
        response = authenticated_client.post(
            '/api/v1/doctor/marketing/',
            {'theme': 'Hack Theme', 'week_start': '2026-03-02'},
            format='json',
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ============================
# DETAIL TESTS
# ============================

@pytest.mark.django_db
class TestMarketingDetail:
    """Tests for campaign detail endpoint."""

    def test_get_detail(self, doctor_client, campaign):
        response = doctor_client.get(f'/api/v1/doctor/marketing/{campaign.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Test Kampanya'
        assert response.data['theme'] == 'Migren Farkindalik Haftasi'
        assert 'content_output' in response.data
        assert 'visual_briefs' in response.data
        assert 'schedule' in response.data

    def test_detail_includes_all_fields(self, doctor_client, campaign):
        response = doctor_client.get(f'/api/v1/doctor/marketing/{campaign.id}/')
        assert response.status_code == status.HTTP_200_OK
        for field in ['id', 'title', 'theme', 'week_start', 'status',
                      'platforms', 'language', 'tone', 'target_audience',
                      'content_output', 'visual_briefs', 'schedule',
                      'editor_notes', 'total_tokens', 'created_at']:
            assert field in response.data

    def test_detail_404_for_nonexistent(self, doctor_client):
        response = doctor_client.get(
            '/api/v1/doctor/marketing/00000000-0000-0000-0000-000000000001/'
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ============================
# UPDATE TESTS
# ============================

@pytest.mark.django_db
class TestMarketingUpdate:
    """Tests for campaign update endpoint."""

    def test_update_editor_notes(self, doctor_client, campaign):
        response = doctor_client.patch(
            f'/api/v1/doctor/marketing/{campaign.id}/',
            {'editor_notes': 'Guncellenmis notlar'},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        campaign.refresh_from_db()
        assert campaign.editor_notes == 'Guncellenmis notlar'

    def test_update_edited_content(self, doctor_client, campaign):
        edited = {'instagram_posts': [{'content': 'Duzenlenmis post'}]}
        response = doctor_client.patch(
            f'/api/v1/doctor/marketing/{campaign.id}/',
            {'edited_content': edited},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        campaign.refresh_from_db()
        assert campaign.edited_content['instagram_posts'][0]['content'] == 'Duzenlenmis post'

    def test_update_status_to_archived(self, doctor_client, campaign):
        response = doctor_client.patch(
            f'/api/v1/doctor/marketing/{campaign.id}/',
            {'status': 'archived'},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        campaign.refresh_from_db()
        assert campaign.status == 'archived'

    def test_update_invalid_status_rejected(self, doctor_client, campaign):
        response = doctor_client.patch(
            f'/api/v1/doctor/marketing/{campaign.id}/',
            {'status': 'published'},
            format='json',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ============================
# APPROVE TESTS
# ============================

@pytest.mark.django_db
class TestMarketingApprove:
    """Tests for campaign approve endpoint."""

    def test_approve_review_campaign(self, doctor_client, campaign):
        response = doctor_client.post(
            f'/api/v1/doctor/marketing/{campaign.id}/approve/'
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'approved'
        campaign.refresh_from_db()
        assert campaign.status == 'approved'
        assert campaign.approved_at is not None

    def test_approve_non_review_campaign_fails(self, doctor_client, generating_campaign):
        response = doctor_client.post(
            f'/api/v1/doctor/marketing/{generating_campaign.id}/approve/'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    def test_approve_already_approved_fails(self, doctor_client, approved_campaign):
        response = doctor_client.post(
            f'/api/v1/doctor/marketing/{approved_campaign.id}/approve/'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_approve_404_for_nonexistent(self, doctor_client):
        response = doctor_client.post(
            '/api/v1/doctor/marketing/00000000-0000-0000-0000-000000000001/approve/'
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_patient_cannot_approve(self, authenticated_client, campaign):
        response = authenticated_client.post(
            f'/api/v1/doctor/marketing/{campaign.id}/approve/'
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ============================
# REGENERATE TESTS
# ============================

@pytest.mark.django_db
class TestMarketingRegenerate:
    """Tests for campaign regenerate endpoint."""

    @patch('apps.doctor_panel.tasks.run_marketing_pipeline')
    def test_regenerate_campaign(self, mock_pipeline, doctor_client, campaign):
        mock_pipeline.delay = MagicMock()
        response = doctor_client.post(
            f'/api/v1/doctor/marketing/{campaign.id}/regenerate/'
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'regenerating'
        campaign.refresh_from_db()
        assert campaign.status == 'generating'
        assert campaign.content_output == {}
        assert campaign.visual_briefs == {}
        assert campaign.schedule == {}

    @patch('apps.doctor_panel.tasks.run_marketing_pipeline')
    def test_regenerate_approved_campaign(self, mock_pipeline, doctor_client, approved_campaign):
        mock_pipeline.delay = MagicMock()
        response = doctor_client.post(
            f'/api/v1/doctor/marketing/{approved_campaign.id}/regenerate/'
        )
        assert response.status_code == status.HTTP_200_OK
        approved_campaign.refresh_from_db()
        assert approved_campaign.status == 'generating'

    def test_regenerate_404(self, doctor_client):
        response = doctor_client.post(
            '/api/v1/doctor/marketing/00000000-0000-0000-0000-000000000001/regenerate/'
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_patient_cannot_regenerate(self, authenticated_client, campaign):
        response = authenticated_client.post(
            f'/api/v1/doctor/marketing/{campaign.id}/regenerate/'
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
