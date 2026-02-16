"""
Integration tests for Social Media API endpoints.
"""

import pytest
from datetime import date, timedelta
from unittest.mock import patch, MagicMock
from django.utils import timezone
from rest_framework import status
from apps.social.models import SocialAccount, SocialCampaign, SocialPost, PublishLog


# ============================
# FIXTURES
# ============================

@pytest.fixture
def social_account(db, doctor_user):
    """Create a test social account."""
    return SocialAccount.objects.create(
        platform='instagram',
        account_name='norosera_test',
        account_id='ig_123',
        access_token='test_token_123',
        connected_by=doctor_user,
        token_expires_at=timezone.now() + timedelta(days=30),
    )


@pytest.fixture
def linkedin_account(db, doctor_user):
    """Create a LinkedIn test account."""
    return SocialAccount.objects.create(
        platform='linkedin',
        account_name='Norosera LI',
        account_id='li_123',
        access_token='li_token_123',
        organization_urn='urn:li:organization:12345',
        connected_by=doctor_user,
        token_expires_at=timezone.now() + timedelta(days=30),
    )


@pytest.fixture
def social_campaign(db, doctor_user):
    """Create a test campaign."""
    return SocialCampaign.objects.create(
        title='Migren Haftasi',
        theme='Migren Tetikleyicileri',
        platforms=['instagram', 'linkedin'],
        status='review',
        created_by=doctor_user,
    )


@pytest.fixture
def social_posts(db, social_campaign, social_account):
    """Create test posts for campaign."""
    posts = []
    for i in range(3):
        posts.append(SocialPost.objects.create(
            campaign=social_campaign,
            platform='instagram',
            caption_tr=f'Test post {i + 1}',
            hashtags=['#test', '#norosera'],
            status='review',
            social_account=social_account,
            scheduled_at=timezone.now() + timedelta(days=i),
        ))
    return posts


# ============================
# AUTH TESTS
# ============================

@pytest.mark.django_db
class TestSocialAuth:
    """Auth and permission tests."""

    def test_unauthenticated_rejected(self, api_client):
        response = api_client.get('/api/v1/social/dashboard/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_patient_cannot_access(self, authenticated_client):
        response = authenticated_client.get('/api/v1/social/dashboard/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_doctor_can_access(self, doctor_client):
        response = doctor_client.get('/api/v1/social/dashboard/')
        assert response.status_code == status.HTTP_200_OK

    def test_admin_cannot_access_doctor_endpoint(self, admin_client):
        response = admin_client.get('/api/v1/social/dashboard/')
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ============================
# ACCOUNT TESTS
# ============================

@pytest.mark.django_db
class TestSocialAccountEndpoints:
    """Tests for social account CRUD."""

    def test_list_accounts(self, doctor_client, social_account):
        response = doctor_client.get('/api/v1/social/accounts/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] >= 1

    def test_create_account(self, doctor_client):
        response = doctor_client.post('/api/v1/social/accounts/', {
            'platform': 'instagram',
            'account_name': 'new_account',
            'account_id': 'new_id',
            'access_token': 'new_token',
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert SocialAccount.objects.filter(account_id='new_id').exists()

    def test_detail_account(self, doctor_client, social_account):
        response = doctor_client.get(f'/api/v1/social/accounts/{social_account.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['account_name'] == 'norosera_test'
        # Token should be masked
        assert 'token_hint' in response.data

    def test_update_account(self, doctor_client, social_account):
        response = doctor_client.patch(
            f'/api/v1/social/accounts/{social_account.id}/',
            {'account_name': 'updated_name'},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        social_account.refresh_from_db()
        assert social_account.account_name == 'updated_name'

    def test_delete_account(self, doctor_client, social_account):
        response = doctor_client.delete(f'/api/v1/social/accounts/{social_account.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not SocialAccount.objects.filter(id=social_account.id).exists()


# ============================
# CAMPAIGN TESTS
# ============================

@pytest.mark.django_db
class TestSocialCampaignEndpoints:
    """Tests for campaign CRUD and workflow."""

    def test_list_campaigns(self, doctor_client, social_campaign):
        response = doctor_client.get('/api/v1/social/campaigns/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] >= 1

    def test_list_campaigns_filter_status(self, doctor_client, social_campaign):
        response = doctor_client.get('/api/v1/social/campaigns/?status=review')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

    def test_list_campaigns_filter_empty(self, doctor_client, social_campaign):
        response = doctor_client.get('/api/v1/social/campaigns/?status=archived')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0

    @patch('apps.social.tasks.run_social_campaign_pipeline')
    def test_create_campaign(self, mock_pipeline, doctor_client):
        mock_pipeline.delay = MagicMock()
        response = doctor_client.post('/api/v1/social/campaigns/', {
            'theme': 'Yeni Tema',
            'platforms': ['instagram'],
            'posts_per_platform': 3,
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert SocialCampaign.objects.filter(theme='Yeni Tema').exists()
        mock_pipeline.delay.assert_called_once()

    def test_detail_campaign(self, doctor_client, social_campaign, social_posts):
        response = doctor_client.get(f'/api/v1/social/campaigns/{social_campaign.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Migren Haftasi'
        assert 'posts' in response.data
        assert len(response.data['posts']) == 3

    @patch('apps.social.tasks.run_social_campaign_pipeline')
    def test_regenerate_campaign(self, mock_pipeline, doctor_client, social_campaign):
        mock_pipeline.delay = MagicMock()
        response = doctor_client.post(f'/api/v1/social/campaigns/{social_campaign.id}/regenerate/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'generating'
        mock_pipeline.delay.assert_called_once()

    def test_regenerate_blocked_when_generating(self, doctor_client, social_campaign):
        social_campaign.status = 'generating'
        social_campaign.save()
        response = doctor_client.post(f'/api/v1/social/campaigns/{social_campaign.id}/regenerate/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_approve_all_posts(self, doctor_client, social_campaign, social_posts):
        response = doctor_client.post(f'/api/v1/social/campaigns/{social_campaign.id}/approve-all/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['approved_count'] == 3

        # Verify all posts are approved
        for post in social_posts:
            post.refresh_from_db()
            assert post.status == 'approved'


# ============================
# POST TESTS
# ============================

@pytest.mark.django_db
class TestSocialPostEndpoints:
    """Tests for post CRUD and workflow."""

    def test_list_posts(self, doctor_client, social_posts):
        response = doctor_client.get('/api/v1/social/posts/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 3

    def test_list_posts_filter_platform(self, doctor_client, social_posts):
        response = doctor_client.get('/api/v1/social/posts/?platform=instagram')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 3

    def test_list_posts_filter_status(self, doctor_client, social_posts):
        response = doctor_client.get('/api/v1/social/posts/?status=review')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 3

    def test_create_manual_post(self, doctor_client):
        response = doctor_client.post('/api/v1/social/posts/', {
            'platform': 'instagram',
            'caption_tr': 'Manuel post',
            'hashtags': ['#test'],
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        post = SocialPost.objects.get(caption_tr='Manuel post')
        assert post.ai_generated is False

    def test_detail_post(self, doctor_client, social_posts):
        post = social_posts[0]
        response = doctor_client.get(f'/api/v1/social/posts/{post.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['caption_tr'] == 'Test post 1'
        assert 'publish_logs' in response.data

    def test_update_post(self, doctor_client, social_posts):
        post = social_posts[0]
        response = doctor_client.patch(f'/api/v1/social/posts/{post.id}/', {
            'edited_caption': 'Duzenlenmis metin',
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        post.refresh_from_db()
        assert post.edited_caption == 'Duzenlenmis metin'

    def test_approve_post(self, doctor_client, social_posts):
        post = social_posts[0]
        response = doctor_client.post(f'/api/v1/social/posts/{post.id}/approve/')
        assert response.status_code == status.HTTP_200_OK
        post.refresh_from_db()
        assert post.status == 'approved'

    def test_approve_already_approved_fails(self, doctor_client, social_posts):
        post = social_posts[0]
        post.status = 'published'
        post.save()
        response = doctor_client.post(f'/api/v1/social/posts/{post.id}/approve/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_schedule_post(self, doctor_client, social_posts, social_account):
        post = social_posts[0]
        post.status = 'approved'
        post.save()

        scheduled = (timezone.now() + timedelta(hours=2)).isoformat()
        response = doctor_client.post(f'/api/v1/social/posts/{post.id}/schedule/', {
            'scheduled_at': scheduled,
            'social_account_id': str(social_account.id),
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        post.refresh_from_db()
        assert post.status == 'scheduled'

    def test_schedule_without_account_fails(self, doctor_client, social_posts):
        post = social_posts[0]
        response = doctor_client.post(f'/api/v1/social/posts/{post.id}/schedule/', {
            'scheduled_at': timezone.now().isoformat(),
        }, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch('apps.social.tasks.retry_failed_post')
    def test_retry_failed_post(self, mock_retry, doctor_client, social_posts):
        mock_retry.delay = MagicMock()
        post = social_posts[0]
        post.status = 'failed'
        post.save()

        response = doctor_client.post(f'/api/v1/social/posts/{post.id}/retry/')
        assert response.status_code == status.HTTP_200_OK
        mock_retry.delay.assert_called_once()

    def test_retry_non_failed_post_rejected(self, doctor_client, social_posts):
        post = social_posts[0]
        response = doctor_client.post(f'/api/v1/social/posts/{post.id}/retry/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ============================
# BULK ACTION TESTS
# ============================

@pytest.mark.django_db
class TestBulkPostActions:
    """Tests for bulk post operations."""

    def test_bulk_approve(self, doctor_client, social_posts):
        ids = [str(p.id) for p in social_posts]
        response = doctor_client.post('/api/v1/social/posts/bulk-action/', {
            'post_ids': ids,
            'action': 'approve',
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['updated'] == 3

    def test_bulk_archive(self, doctor_client, social_posts):
        ids = [str(p.id) for p in social_posts]
        response = doctor_client.post('/api/v1/social/posts/bulk-action/', {
            'post_ids': ids,
            'action': 'archive',
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['updated'] == 3

        for p in social_posts:
            p.refresh_from_db()
            assert p.status == 'archived'

    def test_bulk_invalid_action(self, doctor_client, social_posts):
        response = doctor_client.post('/api/v1/social/posts/bulk-action/', {
            'post_ids': [str(social_posts[0].id)],
            'action': 'invalid',
        }, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ============================
# CALENDAR TESTS
# ============================

@pytest.mark.django_db
class TestSocialCalendar:
    """Tests for calendar endpoint."""

    def test_calendar_returns_posts(self, doctor_client, social_posts):
        now = timezone.now()
        month_str = f'{now.year}-{now.month:02d}'
        response = doctor_client.get(f'/api/v1/social/calendar/?month={month_str}')
        assert response.status_code == status.HTTP_200_OK
        assert 'posts' in response.data
        assert response.data['year'] == now.year
        assert response.data['month'] == now.month

    def test_calendar_default_current_month(self, doctor_client):
        response = doctor_client.get('/api/v1/social/calendar/')
        assert response.status_code == status.HTTP_200_OK
        now = timezone.now()
        assert response.data['year'] == now.year

    def test_calendar_invalid_format(self, doctor_client):
        response = doctor_client.get('/api/v1/social/calendar/?month=invalid')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ============================
# DASHBOARD TESTS
# ============================

@pytest.mark.django_db
class TestSocialDashboard:
    """Tests for dashboard stats."""

    def test_dashboard_returns_stats(self, doctor_client, social_account, social_campaign, social_posts):
        response = doctor_client.get('/api/v1/social/dashboard/')
        assert response.status_code == status.HTTP_200_OK
        assert 'total_accounts' in response.data
        assert 'total_campaigns' in response.data
        assert 'total_posts' in response.data
        assert 'posts_by_platform' in response.data
        assert response.data['total_accounts'] >= 1
        assert response.data['total_posts'] >= 3

    def test_dashboard_empty(self, doctor_client):
        response = doctor_client.get('/api/v1/social/dashboard/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_accounts'] == 0
        assert response.data['total_posts'] == 0


# ============================
# IMAGE PREVIEW TESTS
# ============================

@pytest.mark.django_db
class TestImageEndpoints:
    """Tests for image generation endpoints."""

    def test_image_templates_list(self, doctor_client):
        response = doctor_client.get('/api/v1/social/image-templates/')
        assert response.status_code == status.HTTP_200_OK
        assert 'templates' in response.data
        assert 'sizes' in response.data
        assert len(response.data['templates']) == 3

    def test_image_preview_info_card(self, doctor_client):
        response = doctor_client.post('/api/v1/social/image-preview/', {
            'template': 'info_card',
            'platform': 'instagram',
            'title': 'Test Title',
            'items': ['Item 1', 'Item 2'],
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'image' in response.data
        assert response.data['image'].startswith('data:image/png;base64,')

    def test_image_preview_stat_card(self, doctor_client):
        response = doctor_client.post('/api/v1/social/image-preview/', {
            'template': 'stat_card',
            'platform': 'linkedin',
            'stat_value': '%80',
            'stat_label': 'Test stat',
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'image' in response.data

    def test_image_preview_quote_card(self, doctor_client):
        response = doctor_client.post('/api/v1/social/image-preview/', {
            'template': 'quote_card',
            'quote': 'Test quote text',
            'author': 'Test Author',
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'image' in response.data

    def test_image_preview_invalid_template(self, doctor_client):
        response = doctor_client.post('/api/v1/social/image-preview/', {
            'template': 'nonexistent',
        }, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
