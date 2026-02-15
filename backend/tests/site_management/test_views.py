"""
Integration tests for site management API endpoints.
Tests both public (unauthenticated) and admin (authenticated) endpoints.
"""

import pytest
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from apps.common.models import SiteConfig, FeatureFlag, Announcement, HomepageHero, SocialLink


# ============================
# FIXTURES
# ============================

@pytest.fixture
def site_configs(db):
    """Create test site configs."""
    return [
        SiteConfig.objects.create(key='site_name', label='Site Name', value='TestSite', value_type='string', category='general', is_public=True),
        SiteConfig.objects.create(key='secret_key', label='Secret', value='hidden', value_type='string', category='general', is_public=False),
    ]


@pytest.fixture
def feature_flags(db):
    """Create test feature flags."""
    return [
        FeatureFlag.objects.create(key='migraine_module', label='Migraine', is_enabled=True),
        FeatureFlag.objects.create(key='store_module', label='Store', is_enabled=False),
    ]


@pytest.fixture
def announcements(db):
    """Create test announcements."""
    now = timezone.now()
    return [
        Announcement.objects.create(
            title_tr='Aktif Duyuru', title_en='Active Announcement',
            message_tr='Test mesaji', message_en='Test message',
            is_active=True, priority=1,
        ),
        Announcement.objects.create(
            title_tr='Pasif Duyuru', title_en='Inactive Announcement',
            message_tr='Pasif', message_en='Inactive',
            is_active=False, priority=2,
        ),
        Announcement.objects.create(
            title_tr='Suresi Dolmus', title_en='Expired',
            message_tr='Expired', message_en='Expired',
            is_active=True, priority=3,
            expires_at=now - timedelta(days=1),
        ),
    ]


@pytest.fixture
def heroes(db):
    """Create test homepage heroes."""
    return [
        HomepageHero.objects.create(
            title_tr='Aktif Hero', title_en='Active Hero',
            subtitle_tr='Alt baslik', subtitle_en='Subtitle',
            cta_text_tr='Basla', cta_text_en='Start',
            cta_url='/register', is_active=True,
        ),
        HomepageHero.objects.create(
            title_tr='Pasif Hero', title_en='Inactive Hero',
            subtitle_tr='Alt', subtitle_en='Sub',
            cta_text_tr='X', cta_text_en='X',
            cta_url='/x', is_active=False,
        ),
    ]


@pytest.fixture
def social_links(db):
    """Create test social links."""
    return [
        SocialLink.objects.create(platform='twitter', url='https://twitter.com/test', is_active=True, order=1),
        SocialLink.objects.create(platform='instagram', url='https://instagram.com/test', is_active=True, order=2),
        SocialLink.objects.create(platform='linkedin', url='https://linkedin.com/test', is_active=False, order=3),
    ]


# ============================
# PUBLIC ENDPOINT TESTS
# ============================

@pytest.mark.django_db
class TestPublicSiteConfig:
    """Tests for public site config endpoint."""

    def test_returns_only_public_configs(self, api_client, site_configs):
        response = api_client.get('/api/v1/site/config/public/')
        assert response.status_code == status.HTTP_200_OK
        keys = [c['key'] for c in response.data]
        assert 'site_name' in keys
        assert 'secret_key' not in keys

    def test_no_auth_required(self, api_client, site_configs):
        response = api_client.get('/api/v1/site/config/public/')
        assert response.status_code == status.HTTP_200_OK

    def test_includes_typed_value(self, api_client, site_configs):
        response = api_client.get('/api/v1/site/config/public/')
        assert response.status_code == status.HTTP_200_OK
        site_name = next(c for c in response.data if c['key'] == 'site_name')
        assert 'typed_value' in site_name


@pytest.mark.django_db
class TestActiveAnnouncements:
    """Tests for active announcements endpoint."""

    def test_returns_only_active_valid_announcements(self, api_client, announcements):
        response = api_client.get('/api/v1/site/announcements/active/')
        assert response.status_code == status.HTTP_200_OK
        titles = [a['title_tr'] for a in response.data]
        assert 'Aktif Duyuru' in titles
        assert 'Pasif Duyuru' not in titles
        assert 'Suresi Dolmus' not in titles

    def test_no_auth_required(self, api_client, announcements):
        response = api_client.get('/api/v1/site/announcements/active/')
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestActiveHero:
    """Tests for active hero endpoint."""

    def test_returns_active_hero(self, api_client, heroes):
        response = api_client.get('/api/v1/site/hero/active/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['title_tr'] == 'Aktif Hero'

    def test_no_auth_required(self, api_client, heroes):
        response = api_client.get('/api/v1/site/hero/active/')
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestPublicSocialLinks:
    """Tests for public social links endpoint."""

    def test_returns_only_active_links(self, api_client, social_links):
        response = api_client.get('/api/v1/site/social-links/')
        assert response.status_code == status.HTTP_200_OK
        platforms = [s['platform'] for s in response.data]
        assert 'twitter' in platforms
        assert 'instagram' in platforms
        assert 'linkedin' not in platforms

    def test_includes_platform_display(self, api_client, social_links):
        response = api_client.get('/api/v1/site/social-links/')
        assert response.status_code == status.HTTP_200_OK
        assert all('platform_display' in s for s in response.data)


@pytest.mark.django_db
class TestPublicFeatureFlags:
    """Tests for public feature flags endpoint."""

    def test_returns_all_flags(self, api_client, feature_flags):
        response = api_client.get('/api/v1/site/feature-flags/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_returns_public_fields_only(self, api_client, feature_flags):
        response = api_client.get('/api/v1/site/feature-flags/')
        assert response.status_code == status.HTTP_200_OK
        flag = response.data[0]
        assert 'key' in flag
        assert 'is_enabled' in flag
        assert 'label' in flag


# ============================
# ADMIN ENDPOINT TESTS
# ============================

@pytest.mark.django_db
class TestAdminSiteConfig:
    """Tests for admin site config endpoints."""

    def test_list_requires_admin(self, api_client, site_configs):
        response = api_client.get('/api/v1/site/admin/config/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_patient_cannot_access(self, authenticated_client, site_configs):
        response = authenticated_client.get('/api/v1/site/admin/config/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_list(self, admin_client, site_configs):
        response = admin_client.get('/api/v1/site/admin/config/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_admin_can_update(self, admin_client, site_configs):
        config = site_configs[0]
        response = admin_client.patch(
            f'/api/v1/site/admin/config/{config.id}/',
            {'value': 'UpdatedSite'},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        config.refresh_from_db()
        assert config.value == 'UpdatedSite'


@pytest.mark.django_db
class TestAdminFeatureFlags:
    """Tests for admin feature flag endpoints."""

    def test_admin_can_toggle(self, admin_client, feature_flags):
        flag = feature_flags[1]  # store_module, disabled
        response = admin_client.patch(
            f'/api/v1/site/admin/feature-flags/{flag.id}/',
            {'is_enabled': True},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        flag.refresh_from_db()
        assert flag.is_enabled is True

    def test_doctor_cannot_access(self, doctor_client, feature_flags):
        response = doctor_client.get('/api/v1/site/admin/feature-flags/')
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestAdminAnnouncements:
    """Tests for admin announcement endpoints."""

    def test_admin_can_create(self, admin_client):
        response = admin_client.post(
            '/api/v1/site/admin/announcements/',
            {
                'title_tr': 'Yeni Duyuru',
                'title_en': 'New Announcement',
                'message_tr': 'Yeni mesaj',
                'message_en': 'New message',
                'is_active': True,
                'priority': 1,
            },
            format='json',
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert Announcement.objects.filter(title_tr='Yeni Duyuru').exists()

    def test_admin_can_delete(self, admin_client, announcements):
        ann = announcements[0]
        response = admin_client.delete(f'/api/v1/site/admin/announcements/{ann.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Announcement.objects.filter(id=ann.id).exists()

    def test_patient_cannot_create(self, authenticated_client):
        response = authenticated_client.post(
            '/api/v1/site/admin/announcements/',
            {'title_tr': 'Hack', 'message_tr': 'msg'},
            format='json',
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestAdminHomepageHero:
    """Tests for admin hero endpoints."""

    def test_admin_can_update_hero(self, admin_client, heroes):
        hero = heroes[0]
        response = admin_client.patch(
            f'/api/v1/site/admin/hero/{hero.id}/',
            {'title_tr': 'Guncellenmis Hero'},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        hero.refresh_from_db()
        assert hero.title_tr == 'Guncellenmis Hero'


@pytest.mark.django_db
class TestAdminSocialLinks:
    """Tests for admin social link endpoints."""

    def test_admin_can_update_url(self, admin_client, social_links):
        link = social_links[0]
        response = admin_client.patch(
            f'/api/v1/site/admin/social-links/{link.id}/',
            {'url': 'https://twitter.com/norosera_updated'},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        link.refresh_from_db()
        assert link.url == 'https://twitter.com/norosera_updated'

    def test_admin_can_toggle_active(self, admin_client, social_links):
        link = social_links[2]  # linkedin, inactive
        response = admin_client.patch(
            f'/api/v1/site/admin/social-links/{link.id}/',
            {'is_active': True},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        link.refresh_from_db()
        assert link.is_active is True


# ============================
# DASHBOARD STATS
# ============================

@pytest.mark.django_db
class TestDashboardStats:
    """Tests for dashboard stats endpoint."""

    def test_requires_admin(self, api_client):
        response = api_client.get('/api/v1/site/admin/dashboard-stats/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_admin_can_get_stats(self, admin_client, feature_flags, announcements):
        response = admin_client.get('/api/v1/site/admin/dashboard-stats/')
        assert response.status_code == status.HTTP_200_OK
        assert 'total_users' in response.data
        assert 'total_patients' in response.data
        assert 'feature_flags_on' in response.data
        assert 'active_announcements' in response.data

    def test_stats_counts_are_correct(self, admin_client, feature_flags, announcements):
        response = admin_client.get('/api/v1/site/admin/dashboard-stats/')
        assert response.data['feature_flags_on'] == 1
        assert response.data['feature_flags_off'] == 1
        assert response.data['active_announcements'] == 2  # 2 active (incl. expired — model is_active)

    def test_patient_cannot_get_stats(self, authenticated_client):
        response = authenticated_client.get('/api/v1/site/admin/dashboard-stats/')
        assert response.status_code == status.HTTP_403_FORBIDDEN
