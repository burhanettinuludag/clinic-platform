"""
Doctor Panel Celery Tasks.

Marketing pipeline ve diger async islemler.
"""

import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2)
def run_marketing_pipeline(self, campaign_id: str):
    """
    Marketing pipeline'ini calistir.

    3 adimli pipeline:
    1. MarketingContentAgent: Post metinleri uret
    2. VisualBriefAgent: Gorsel brief'ler olustur
    3. SchedulingAgent: Haftalik yayin plani
    """
    from apps.common.models import MarketingCampaign

    try:
        campaign = MarketingCampaign.objects.get(id=campaign_id)
    except MarketingCampaign.DoesNotExist:
        logger.error(f"MarketingCampaign {campaign_id} bulunamadi")
        return

    from services.orchestrator import orchestrator
    from services.registry import agent_registry

    input_data = {
        'theme': campaign.theme,
        'platforms': campaign.platforms or ['instagram', 'linkedin', 'twitter'],
        'posts_per_platform': 3,
        'language': campaign.language,
        'tone': campaign.tone,
        'target_audience': campaign.target_audience,
        'include_video_script': True,
        'week_start': str(campaign.week_start),
    }

    total_tokens = 0

    try:
        # Step 1: Icerik uret
        result = orchestrator.run_chain(
            'marketing_content_only',
            input_data,
            triggered_by=campaign.created_by,
        )

        if result.success and result.step_results:
            content_data = result.step_results[0].data
            campaign.content_output = content_data
            total_tokens += result.step_results[0].tokens_used

            # Postlari duz listeye cevir (visual brief ve scheduling icin)
            flat_posts = []
            for platform in ['instagram', 'linkedin', 'twitter']:
                for post in content_data.get(f'{platform}_posts', []):
                    post_copy = dict(post)
                    post_copy['platform'] = platform
                    flat_posts.append(post_copy)

            # Step 2: Gorsel brief
            if 'visual_brief_agent' in agent_registry:
                brief_agent = agent_registry.get('visual_brief_agent')
                brief_result = brief_agent.run(
                    {'posts': flat_posts, 'theme': campaign.theme},
                    triggered_by=campaign.created_by,
                )
                if brief_result.success:
                    campaign.visual_briefs = brief_result.data
                total_tokens += brief_result.tokens_used

            # Step 3: Zamanlama
            if 'scheduling_agent' in agent_registry:
                sched_agent = agent_registry.get('scheduling_agent')
                sched_result = sched_agent.run(
                    {
                        'posts': flat_posts,
                        'week_start': str(campaign.week_start),
                        'platforms': campaign.platforms or ['instagram', 'linkedin', 'twitter'],
                    },
                    triggered_by=campaign.created_by,
                )
                if sched_result.success:
                    campaign.schedule = sched_result.data
                total_tokens += sched_result.tokens_used

            campaign.total_tokens = total_tokens
            campaign.status = 'review'
        else:
            campaign.status = 'review'
            if result.step_results:
                campaign.content_output = result.step_results[0].data
            campaign.editor_notes = f"Pipeline kismi basarili: {result.error}"

    except Exception as e:
        logger.exception(f"Marketing pipeline hatasi: campaign={campaign_id}")
        campaign.editor_notes = f"Pipeline hatasi: {str(e)}"
        campaign.status = 'review'

    campaign.save()
