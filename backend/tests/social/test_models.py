"""
Unit tests for Social Media models.
"""

import pytest
from datetime import date, timedelta
from django.utils import timezone
from apps.social.models import SocialAccount, SocialCampaign, SocialPost, PublishLog


@pytest.mark.django_db
class TestSocialAccountModel:
    """Tests for SocialAccount model."""

    def test_create_account(self, doctor_user):
        acc = SocialAccount.objects.create(
            platform='instagram',
            account_name='norosera_ig',
            account_id='12345',
            access_token='test_token',
            connected_by=doctor_user,
        )
        assert acc.platform == 'instagram'
        assert acc.account_name == 'norosera_ig'
        assert acc.id is not None

    def test_default_status_is_active(self, doctor_user):
        acc = SocialAccount.objects.create(
            platform='instagram', account_name='test', account_id='1',
            access_token='tok', connected_by=doctor_user,
        )
        assert acc.status == 'active'

    def test_str_representation(self, doctor_user):
        acc = SocialAccount.objects.create(
            platform='linkedin', account_name='Norosera LI', account_id='li1',
            access_token='tok', connected_by=doctor_user,
        )
        result = str(acc)
        assert 'LinkedIn' in result
        assert 'Norosera LI' in result

    def test_is_token_valid_true(self, doctor_user):
        acc = SocialAccount.objects.create(
            platform='instagram', account_name='test', account_id='2',
            access_token='tok', connected_by=doctor_user,
            token_expires_at=timezone.now() + timedelta(days=30),
        )
        assert acc.is_token_valid is True

    def test_is_token_valid_false(self, doctor_user):
        acc = SocialAccount.objects.create(
            platform='instagram', account_name='test', account_id='3',
            access_token='tok', connected_by=doctor_user,
            token_expires_at=timezone.now() - timedelta(days=1),
        )
        assert acc.is_token_valid is False

    def test_is_token_valid_no_expiry(self, doctor_user):
        acc = SocialAccount.objects.create(
            platform='instagram', account_name='test', account_id='4',
            access_token='tok', connected_by=doctor_user,
        )
        assert acc.is_token_valid is True

    def test_unique_together(self, doctor_user):
        SocialAccount.objects.create(
            platform='instagram', account_name='test', account_id='unique1',
            access_token='tok', connected_by=doctor_user,
        )
        with pytest.raises(Exception):
            SocialAccount.objects.create(
                platform='instagram', account_name='test2', account_id='unique1',
                access_token='tok2', connected_by=doctor_user,
            )

    def test_default_counters(self, doctor_user):
        acc = SocialAccount.objects.create(
            platform='instagram', account_name='test', account_id='5',
            access_token='tok', connected_by=doctor_user,
        )
        assert acc.total_posts_published == 0
        assert acc.followers_count == 0


@pytest.mark.django_db
class TestSocialCampaignModel:
    """Tests for SocialCampaign model."""

    def test_create_campaign(self, doctor_user):
        c = SocialCampaign.objects.create(
            title='Migren Haftasi', theme='Migren Tetikleyicileri',
            created_by=doctor_user,
        )
        assert c.title == 'Migren Haftasi'
        assert c.id is not None

    def test_default_status_is_draft(self, doctor_user):
        c = SocialCampaign.objects.create(
            title='Test', theme='Test', created_by=doctor_user,
        )
        assert c.status == 'draft'

    def test_default_json_fields(self, doctor_user):
        c = SocialCampaign.objects.create(
            title='Test', theme='Test', created_by=doctor_user,
        )
        assert c.platforms == []
        assert c.content_output == {}
        assert c.schedule_output == {}

    def test_str_representation(self, doctor_user):
        c = SocialCampaign.objects.create(
            title='Kampanya', theme='tema', status='review',
            created_by=doctor_user,
        )
        result = str(c)
        assert 'Kampanya' in result

    def test_post_stats_property(self, doctor_user):
        c = SocialCampaign.objects.create(
            title='Stats Test', theme='tema', created_by=doctor_user,
        )
        SocialPost.objects.create(
            campaign=c, platform='instagram', caption_tr='Post 1', status='review',
        )
        SocialPost.objects.create(
            campaign=c, platform='instagram', caption_tr='Post 2', status='approved',
        )
        stats = c.post_stats
        assert stats['total'] == 2
        assert stats['review'] == 1
        assert stats['approved'] == 1

    def test_ordering_by_created_desc(self, doctor_user):
        c1 = SocialCampaign.objects.create(
            title='Old', theme='t', created_by=doctor_user,
        )
        c2 = SocialCampaign.objects.create(
            title='New', theme='t', created_by=doctor_user,
        )
        campaigns = list(SocialCampaign.objects.all())
        assert campaigns[0].id == c2.id

    def test_default_tokens_and_cost(self, doctor_user):
        c = SocialCampaign.objects.create(
            title='Test', theme='t', created_by=doctor_user,
        )
        assert c.total_tokens == 0
        assert c.total_cost_usd == 0

    def test_created_by_set_null(self, doctor_user):
        c = SocialCampaign.objects.create(
            title='Test', theme='t', created_by=doctor_user,
        )
        doctor_user.delete()
        c.refresh_from_db()
        assert c.created_by is None


@pytest.mark.django_db
class TestSocialPostModel:
    """Tests for SocialPost model."""

    def test_create_post(self):
        p = SocialPost.objects.create(
            platform='instagram', caption_tr='Test post',
        )
        assert p.platform == 'instagram'
        assert p.id is not None

    def test_default_status_is_draft(self):
        p = SocialPost.objects.create(
            platform='instagram', caption_tr='Test',
        )
        assert p.status == 'draft'

    def test_default_format_is_single_image(self):
        p = SocialPost.objects.create(
            platform='instagram', caption_tr='Test',
        )
        assert p.post_format == 'single_image'

    def test_final_caption_returns_original(self):
        p = SocialPost.objects.create(
            platform='instagram', caption_tr='Original text',
        )
        assert p.final_caption == 'Original text'

    def test_final_caption_returns_edited(self):
        p = SocialPost.objects.create(
            platform='instagram', caption_tr='Original',
            edited_caption='Edited text',
        )
        assert p.final_caption == 'Edited text'

    def test_final_caption_with_hashtags(self):
        p = SocialPost.objects.create(
            platform='instagram', caption_tr='Caption',
            hashtags=['#norosera', '#saglik'],
        )
        result = p.final_caption_with_hashtags
        assert 'Caption' in result
        assert '#norosera' in result
        assert '#saglik' in result

    def test_str_representation(self):
        p = SocialPost.objects.create(
            platform='instagram', caption_tr='Test caption for display',
        )
        result = str(p)
        assert 'Instagram' in result

    def test_default_json_fields(self):
        p = SocialPost.objects.create(
            platform='instagram', caption_tr='Test',
        )
        assert p.hashtags == []
        assert p.image_urls == []
        assert p.visual_brief == {}

    def test_ai_generated_default_true(self):
        p = SocialPost.objects.create(
            platform='instagram', caption_tr='Test',
        )
        assert p.ai_generated is True

    def test_campaign_foreign_key(self, doctor_user):
        c = SocialCampaign.objects.create(
            title='Camp', theme='t', created_by=doctor_user,
        )
        p = SocialPost.objects.create(
            campaign=c, platform='instagram', caption_tr='Test',
        )
        assert p.campaign == c
        assert c.posts.count() == 1


@pytest.mark.django_db
class TestPublishLogModel:
    """Tests for PublishLog model."""

    def test_create_log(self):
        post = SocialPost.objects.create(
            platform='instagram', caption_tr='Test',
        )
        log = PublishLog.objects.create(
            post=post, action='publish', success=True,
        )
        assert log.action == 'publish'
        assert log.success is True

    def test_str_representation(self):
        post = SocialPost.objects.create(
            platform='instagram', caption_tr='Test',
        )
        log = PublishLog.objects.create(
            post=post, action='publish', success=False,
            error_message='Token expired',
        )
        result = str(log)
        assert 'FAIL' in result

    def test_log_ordering(self):
        post = SocialPost.objects.create(
            platform='instagram', caption_tr='Test',
        )
        log1 = PublishLog.objects.create(post=post, action='try1', success=False)
        log2 = PublishLog.objects.create(post=post, action='try2', success=True)
        logs = list(PublishLog.objects.filter(post=post))
        assert logs[0].id == log2.id  # newest first
