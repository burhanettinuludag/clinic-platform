"""
Unit tests for MarketingCampaign model.
"""

import pytest
from datetime import date
from apps.common.models import MarketingCampaign


@pytest.mark.django_db
class TestMarketingCampaignModel:
    """Tests for MarketingCampaign model."""

    def test_create_campaign(self):
        campaign = MarketingCampaign.objects.create(
            title='Migren Farkindalik',
            theme='Migren Farkindalik Haftasi',
            week_start=date(2026, 3, 2),
        )
        assert campaign.title == 'Migren Farkindalik'
        assert campaign.theme == 'Migren Farkindalik Haftasi'
        assert campaign.week_start == date(2026, 3, 2)
        assert campaign.id is not None

    def test_default_status_is_generating(self):
        campaign = MarketingCampaign.objects.create(
            title='Test', theme='Test tema', week_start=date(2026, 3, 2),
        )
        assert campaign.status == 'generating'

    def test_default_language_is_tr(self):
        campaign = MarketingCampaign.objects.create(
            title='Test', theme='Test tema', week_start=date(2026, 3, 2),
        )
        assert campaign.language == 'tr'

    def test_default_tone_is_educational(self):
        campaign = MarketingCampaign.objects.create(
            title='Test', theme='Test tema', week_start=date(2026, 3, 2),
        )
        assert campaign.tone == 'educational'

    def test_default_target_audience_is_patients(self):
        campaign = MarketingCampaign.objects.create(
            title='Test', theme='Test tema', week_start=date(2026, 3, 2),
        )
        assert campaign.target_audience == 'patients'

    def test_default_json_fields_are_empty(self):
        campaign = MarketingCampaign.objects.create(
            title='Test', theme='Test tema', week_start=date(2026, 3, 2),
        )
        assert campaign.content_output == {}
        assert campaign.visual_briefs == {}
        assert campaign.schedule == {}
        assert campaign.edited_content == {}
        assert campaign.platforms == []

    def test_default_tokens_and_cost(self):
        campaign = MarketingCampaign.objects.create(
            title='Test', theme='Test tema', week_start=date(2026, 3, 2),
        )
        assert campaign.total_tokens == 0
        assert campaign.total_cost_usd == 0

    def test_str_representation(self):
        campaign = MarketingCampaign.objects.create(
            title='Migren Hafta', theme='Migren', week_start=date(2026, 3, 2),
            status='review',
        )
        result = str(campaign)
        assert 'Inceleme Bekliyor' in result
        assert 'Migren Hafta' in result
        assert '2026-03-02' in result

    def test_str_with_generating_status(self):
        campaign = MarketingCampaign.objects.create(
            title='Test', theme='Test', week_start=date(2026, 3, 2),
        )
        assert 'Uretiyor' in str(campaign)

    def test_ordering_by_week_start_desc(self):
        c1 = MarketingCampaign.objects.create(
            title='Old', theme='Old', week_start=date(2026, 2, 1),
        )
        c2 = MarketingCampaign.objects.create(
            title='New', theme='New', week_start=date(2026, 3, 1),
        )
        campaigns = list(MarketingCampaign.objects.all())
        assert campaigns[0].id == c2.id
        assert campaigns[1].id == c1.id

    def test_platforms_json_field(self):
        campaign = MarketingCampaign.objects.create(
            title='Test', theme='Test', week_start=date(2026, 3, 2),
            platforms=['instagram', 'linkedin'],
        )
        campaign.refresh_from_db()
        assert campaign.platforms == ['instagram', 'linkedin']

    def test_status_choices(self):
        for status_code, _ in MarketingCampaign.STATUS_CHOICES:
            campaign = MarketingCampaign.objects.create(
                title=f'Test {status_code}', theme='Test',
                week_start=date(2026, 3, 2), status=status_code,
            )
            assert campaign.status == status_code

    def test_created_by_foreign_key(self, doctor_user):
        campaign = MarketingCampaign.objects.create(
            title='Test', theme='Test', week_start=date(2026, 3, 2),
            created_by=doctor_user,
        )
        assert campaign.created_by == doctor_user

    def test_created_by_null_on_delete(self, doctor_user):
        campaign = MarketingCampaign.objects.create(
            title='Test', theme='Test', week_start=date(2026, 3, 2),
            created_by=doctor_user,
        )
        doctor_user.delete()
        campaign.refresh_from_db()
        assert campaign.created_by is None

    def test_approved_at_null_by_default(self):
        campaign = MarketingCampaign.objects.create(
            title='Test', theme='Test', week_start=date(2026, 3, 2),
        )
        assert campaign.approved_at is None

    def test_content_output_stores_json(self):
        data = {
            'instagram_posts': [{'content': 'Test post', 'hashtags': ['#test']}],
            'linkedin_posts': [],
        }
        campaign = MarketingCampaign.objects.create(
            title='Test', theme='Test', week_start=date(2026, 3, 2),
            content_output=data,
        )
        campaign.refresh_from_db()
        assert campaign.content_output['instagram_posts'][0]['content'] == 'Test post'

    def test_editor_notes_blank_by_default(self):
        campaign = MarketingCampaign.objects.create(
            title='Test', theme='Test', week_start=date(2026, 3, 2),
        )
        assert campaign.editor_notes == ''
