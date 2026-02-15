"""
Unit tests for site management models: SiteConfig, FeatureFlag, Announcement, HomepageHero, SocialLink.
"""

import pytest
from django.utils import timezone
from datetime import timedelta
from apps.common.models import SiteConfig, FeatureFlag, Announcement, HomepageHero, SocialLink


@pytest.mark.django_db
class TestSiteConfig:
    """Tests for SiteConfig model."""

    def test_create_string_config(self):
        config = SiteConfig.objects.create(
            key='test_key',
            label='Test Label',
            value='test_value',
            value_type='string',
            category='general',
            is_public=True,
        )
        assert str(config) == 'test_key = test_value'
        assert config.value == 'test_value'

    def test_create_boolean_config(self):
        config = SiteConfig.objects.create(
            key='test_bool',
            label='Test Boolean',
            value='true',
            value_type='boolean',
            category='general',
            is_public=True,
        )
        assert config.value == 'true'
        assert config.value_type == 'boolean'

    def test_unique_key_constraint(self):
        SiteConfig.objects.create(key='unique_key', label='First', value='1', value_type='string', category='general')
        with pytest.raises(Exception):
            SiteConfig.objects.create(key='unique_key', label='Second', value='2', value_type='string', category='general')

    def test_default_values(self):
        config = SiteConfig.objects.create(key='defaults', label='Defaults', value='val', value_type='string', category='general')
        assert config.is_public is False  # default is False
        assert config.description == ''


@pytest.mark.django_db
class TestFeatureFlag:
    """Tests for FeatureFlag model."""

    def test_create_feature_flag(self):
        flag = FeatureFlag.objects.create(
            key='test_flag',
            label='Test Flag',
            is_enabled=True,
            description='A test feature flag',
        )
        assert str(flag) == 'test_flag [ON]'
        assert flag.is_enabled is True

    def test_default_disabled(self):
        flag = FeatureFlag.objects.create(key='disabled_flag', label='Disabled')
        assert flag.is_enabled is False

    def test_unique_key(self):
        FeatureFlag.objects.create(key='unique_flag', label='First')
        with pytest.raises(Exception):
            FeatureFlag.objects.create(key='unique_flag', label='Second')


@pytest.mark.django_db
class TestAnnouncement:
    """Tests for Announcement model."""

    def test_create_announcement(self):
        ann = Announcement.objects.create(
            title_tr='Test Duyuru',
            title_en='Test Announcement',
            message_tr='Bu bir test duyurusudur.',
            message_en='This is a test announcement.',
            is_active=True,
            priority=1,
        )
        assert 'Test Duyuru' in str(ann)
        assert ann.is_active is True
        assert ann.priority == 1

    def test_default_colors(self):
        ann = Announcement.objects.create(
            title_tr='Renk Test',
            message_tr='Renk testi',
        )
        assert ann.bg_color == '#1B4F72'
        assert ann.text_color == '#FFFFFF'

    def test_date_filtering(self):
        now = timezone.now()
        # Future announcement
        future = Announcement.objects.create(
            title_tr='Gelecek', message_tr='msg',
            is_active=True, starts_at=now + timedelta(days=1)
        )
        # Expired announcement
        expired = Announcement.objects.create(
            title_tr='Gecmis', message_tr='msg',
            is_active=True, expires_at=now - timedelta(days=1)
        )
        # Active announcement
        active = Announcement.objects.create(
            title_tr='Aktif', message_tr='msg',
            is_active=True,
            starts_at=now - timedelta(days=1),
            expires_at=now + timedelta(days=1),
        )

        qs = Announcement.objects.filter(is_active=True)
        qs = qs.exclude(starts_at__gt=now)
        qs = qs.exclude(expires_at__lt=now)
        ids = list(qs.values_list('id', flat=True))
        assert active.id in ids
        assert future.id not in ids
        assert expired.id not in ids


@pytest.mark.django_db
class TestHomepageHero:
    """Tests for HomepageHero model."""

    def test_create_hero(self):
        hero = HomepageHero.objects.create(
            title_tr='Ana Baslik',
            title_en='Main Title',
            subtitle_tr='Alt baslik',
            subtitle_en='Subtitle',
            cta_text_tr='Basla',
            cta_text_en='Start',
            cta_url='/auth/register',
            is_active=True,
        )
        assert str(hero) == 'Ana Baslik'
        assert hero.is_active is True

    def test_only_one_active_hero(self):
        """Multiple heroes can exist but only one should be active (business logic)."""
        HomepageHero.objects.create(title_tr='Hero 1', is_active=True)
        HomepageHero.objects.create(title_tr='Hero 2', is_active=True)
        # Both exist - business logic should be in views to pick first
        active_count = HomepageHero.objects.filter(is_active=True).count()
        assert active_count == 2  # Model doesn't enforce single active


@pytest.mark.django_db
class TestSocialLink:
    """Tests for SocialLink model."""

    def test_create_social_link(self):
        link = SocialLink.objects.create(
            platform='twitter',
            url='https://twitter.com/test',
            is_active=True,
            order=1,
        )
        assert 'Twitter / X' in str(link)
        assert link.is_active is True

    def test_platform_choices(self):
        """All platform choices should be valid."""
        valid_platforms = ['twitter', 'linkedin', 'instagram', 'youtube', 'facebook', 'tiktok', 'github']
        for platform in valid_platforms:
            link = SocialLink.objects.create(
                platform=platform,
                url=f'https://{platform}.com/test',
                is_active=True,
                order=1,
            )
            assert link.platform == platform

    def test_ordering(self):
        SocialLink.objects.create(platform='youtube', url='https://youtube.com', order=3)
        SocialLink.objects.create(platform='twitter', url='https://twitter.com', order=1)
        SocialLink.objects.create(platform='instagram', url='https://instagram.com', order=2)
        links = list(SocialLink.objects.values_list('platform', flat=True))
        assert links == ['twitter', 'instagram', 'youtube']
