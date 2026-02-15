"""
Social Media Celery Tasks.

1. run_social_campaign_pipeline — AI icerik + zamanlama uretim pipeline'i
2. publish_scheduled_posts      — Zamanlanan postlari yayinla (her 5 dk)
3. refresh_social_tokens        — Token yenileme (gunluk)
4. retry_failed_post            — Basarisiz post'u tekrar dene
"""

import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


# =============================================================================
# 1) SOCIAL CAMPAIGN PIPELINE
# =============================================================================

@shared_task(bind=True, max_retries=2)
def run_social_campaign_pipeline(self, campaign_id: str):
    """
    Sosyal medya kampanyasi icin AI pipeline calistir.

    1. MarketingContentAgent → Post metinleri uret
    2. VisualBriefAgent → Gorsel brief'leri olustur
    3. SchedulingAgent → Haftalik zamanlama plani

    Sonuclari SocialCampaign'e kaydet ve SocialPost objeleri olustur.
    """
    from apps.social.models import SocialCampaign, SocialPost

    try:
        campaign = SocialCampaign.objects.get(id=campaign_id)
    except SocialCampaign.DoesNotExist:
        logger.error(f"SocialCampaign {campaign_id} bulunamadi")
        return

    # Durumu 'generating' yap
    campaign.status = 'generating'
    campaign.save(update_fields=['status'])

    from services.orchestrator import orchestrator
    from services.registry import agent_registry

    input_data = {
        'theme': campaign.theme,
        'platforms': campaign.platforms or ['instagram', 'linkedin'],
        'posts_per_platform': campaign.posts_per_platform,
        'language': campaign.language,
        'tone': campaign.tone,
        'target_audience': campaign.target_audience,
        'include_video_script': False,
        'week_start': str(campaign.week_start) if campaign.week_start else '',
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

            # Postlari duz listeye cevir
            flat_posts = []
            for platform in campaign.platforms or ['instagram', 'linkedin']:
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
                    campaign.content_output['visual_briefs'] = brief_result.data
                total_tokens += brief_result.tokens_used

            # Step 3: Zamanlama
            schedule_data = {}
            if 'scheduling_agent' in agent_registry:
                sched_agent = agent_registry.get('scheduling_agent')
                sched_result = sched_agent.run(
                    {
                        'posts': flat_posts,
                        'week_start': str(campaign.week_start) if campaign.week_start else '',
                        'platforms': campaign.platforms or ['instagram', 'linkedin'],
                    },
                    triggered_by=campaign.created_by,
                )
                if sched_result.success:
                    schedule_data = sched_result.data
                    campaign.schedule_output = schedule_data
                total_tokens += sched_result.tokens_used

            # SocialPost objeleri olustur
            _create_posts_from_pipeline(campaign, flat_posts, schedule_data)

            campaign.total_tokens = total_tokens
            campaign.status = 'review'
        else:
            campaign.status = 'review'
            if result.step_results:
                campaign.content_output = result.step_results[0].data
            logger.warning(f"Social pipeline kismi basarili: campaign={campaign_id}, error={result.error}")

    except Exception as e:
        logger.exception(f"Social pipeline hatasi: campaign={campaign_id}")
        campaign.status = 'review'

    campaign.save()


def _create_posts_from_pipeline(campaign, flat_posts, schedule_data):
    """
    Pipeline ciktisinda her post icin SocialPost olustur.
    Schedule varsa scheduled_at ayarla.
    """
    from apps.social.models import SocialPost
    from django.utils import timezone as tz
    from datetime import datetime

    # Schedule'dan zamanlama bilgisini cek
    schedule_map = {}  # (platform, post_index) -> datetime
    if schedule_data:
        for day_entry in schedule_data.get('schedule', []):
            date_str = day_entry.get('date', '')
            for slot in day_entry.get('slots', []):
                time_str = slot.get('time', '')
                platform = slot.get('platform', '')
                post_index = slot.get('post_index', -1)
                if date_str and time_str and post_index >= 0:
                    try:
                        dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
                        schedule_map[(platform, post_index)] = tz.make_aware(dt)
                    except (ValueError, TypeError):
                        pass

    for idx, post_data in enumerate(flat_posts):
        platform = post_data.get('platform', 'instagram')

        # Hashtag'leri al
        hashtags = post_data.get('hashtags', [])
        if isinstance(hashtags, str):
            hashtags = [h.strip() for h in hashtags.split() if h.startswith('#')]

        # Caption
        caption = post_data.get('text', '') or post_data.get('text_tr', '')

        # Format
        suggested = post_data.get('suggested_format', 'single_image')
        format_map = {
            'carousel': 'carousel',
            'single': 'single_image',
            'single_image': 'single_image',
            'reel': 'reel',
            'video': 'video',
            'story': 'story',
            'text_only': 'text_only',
        }
        post_format = format_map.get(suggested, 'single_image')

        # Scheduled at
        scheduled_at = schedule_map.get((platform, idx))

        SocialPost.objects.create(
            campaign=campaign,
            platform=platform,
            post_format=post_format,
            caption_tr=caption,
            caption_en=post_data.get('text_en', ''),
            hashtags=hashtags,
            image_prompt=post_data.get('image_prompt', ''),
            visual_brief=post_data.get('visual_brief', {}),
            scheduled_at=scheduled_at,
            status='review',
            ai_generated=True,
            tokens_used=0,
            created_by=campaign.created_by,
        )


# =============================================================================
# 2) PUBLISH SCHEDULED POSTS (her 5 dakika)
# =============================================================================

@shared_task(bind=True, max_retries=1)
def publish_scheduled_posts(self):
    """
    Zamanlanmis ve onaylanmis postlari yayinla.
    Her 5 dakikada calisan periodic task.
    """
    from apps.social.models import SocialPost, SocialAccount, PublishLog
    from apps.social.publishers import get_publisher

    now = timezone.now()
    window = now + timedelta(minutes=5)

    # Zamani gelen scheduled postlari bul
    posts = SocialPost.objects.filter(
        status='scheduled',
        scheduled_at__lte=window,
        social_account__isnull=False,
    ).select_related('social_account')

    published_count = 0
    failed_count = 0

    for post in posts:
        account = post.social_account

        # Token gecerliligi kontrol
        if not account.is_token_valid:
            PublishLog.objects.create(
                post=post,
                action='publish',
                success=False,
                error_message=f'Token suresi dolmus: {account.account_name}',
            )
            post.status = 'failed'
            post.publish_error = 'Token suresi dolmus'
            post.save(update_fields=['status', 'publish_error'])
            failed_count += 1
            continue

        # Yayinla
        post.status = 'publishing'
        post.save(update_fields=['status'])

        try:
            publisher = get_publisher(account)
            result = publisher.publish(post)

            PublishLog.objects.create(
                post=post,
                action='publish',
                success=result.success,
                response_data=result.response_data,
                error_message=result.error,
            )

            if result.success:
                post.status = 'published'
                post.published_at = timezone.now()
                post.platform_post_id = result.platform_post_id
                post.platform_url = result.platform_url
                post.publish_error = ''
                post.save(update_fields=[
                    'status', 'published_at', 'platform_post_id',
                    'platform_url', 'publish_error',
                ])

                # Hesap istatistiklerini guncelle
                account.total_posts_published += 1
                account.last_used_at = timezone.now()
                account.save(update_fields=['total_posts_published', 'last_used_at'])

                published_count += 1
            else:
                post.status = 'failed'
                post.publish_error = result.error
                post.save(update_fields=['status', 'publish_error'])
                failed_count += 1

        except Exception as e:
            logger.exception(f"Post publish hatasi: post={post.id}")
            post.status = 'failed'
            post.publish_error = str(e)
            post.save(update_fields=['status', 'publish_error'])

            PublishLog.objects.create(
                post=post,
                action='publish',
                success=False,
                error_message=str(e),
            )
            failed_count += 1

    logger.info(f"Scheduled publish: {published_count} basarili, {failed_count} basarisiz")
    return {
        'published': published_count,
        'failed': failed_count,
    }


# =============================================================================
# 3) REFRESH SOCIAL TOKENS (gunluk)
# =============================================================================

@shared_task(bind=True, max_retries=1)
def refresh_social_tokens(self):
    """
    Suresi yaklasan token'lari yenile.
    Instagram long-lived token: 60 gun gecerli, 7 gun kala yenile.
    LinkedIn token: 60 gun gecerli, 7 gun kala yenile.
    """
    from apps.social.models import SocialAccount
    from apps.social.publishers import get_publisher

    threshold = timezone.now() + timedelta(days=7)

    accounts = SocialAccount.objects.filter(
        status='active',
        token_expires_at__isnull=False,
        token_expires_at__lte=threshold,
    )

    refreshed = 0
    failed = 0

    for account in accounts:
        try:
            publisher = get_publisher(account)

            if hasattr(publisher, 'refresh_token') and callable(publisher.refresh_token):
                new_token = publisher.refresh_token()
                if new_token:
                    account.access_token = new_token
                    account.token_expires_at = timezone.now() + timedelta(days=60)
                    account.status = 'active'
                    account.save(update_fields=['access_token', 'token_expires_at', 'status'])
                    refreshed += 1
                    logger.info(f"Token yenilendi: {account.platform} - {account.account_name}")
                else:
                    account.status = 'expired'
                    account.save(update_fields=['status'])
                    failed += 1
                    logger.warning(f"Token yenilenemedi: {account.platform} - {account.account_name}")
            else:
                # Publisher token refresh desteklemiyor
                logger.info(f"Token refresh desteklenmiyor: {account.platform}")

        except Exception as e:
            logger.exception(f"Token refresh hatasi: {account.id}")
            failed += 1

    logger.info(f"Token refresh: {refreshed} basarili, {failed} basarisiz")
    return {
        'refreshed': refreshed,
        'failed': failed,
    }


# =============================================================================
# 4) RETRY FAILED POST
# =============================================================================

@shared_task(bind=True, max_retries=3)
def retry_failed_post(self, post_id: str):
    """
    Basarisiz olan bir postu tekrar yayinlamayi dene.
    Max 3 deneme, artan bekleme suresiyle.
    """
    from apps.social.models import SocialPost, PublishLog
    from apps.social.publishers import get_publisher

    try:
        post = SocialPost.objects.select_related('social_account').get(id=post_id)
    except SocialPost.DoesNotExist:
        logger.error(f"SocialPost {post_id} bulunamadi")
        return

    if post.status == 'published':
        logger.info(f"Post zaten yayinlanmis: {post_id}")
        return

    account = post.social_account
    if not account:
        post.publish_error = 'Sosyal medya hesabi atanmamis'
        post.save(update_fields=['publish_error'])
        return

    if not account.is_token_valid:
        post.publish_error = 'Token suresi dolmus, once token yenilemesi gerekli'
        post.save(update_fields=['publish_error'])
        return

    post.status = 'publishing'
    post.save(update_fields=['status'])

    try:
        publisher = get_publisher(account)
        result = publisher.publish(post)

        PublishLog.objects.create(
            post=post,
            action='retry',
            success=result.success,
            response_data=result.response_data,
            error_message=result.error,
        )

        if result.success:
            post.status = 'published'
            post.published_at = timezone.now()
            post.platform_post_id = result.platform_post_id
            post.platform_url = result.platform_url
            post.publish_error = ''
            post.save(update_fields=[
                'status', 'published_at', 'platform_post_id',
                'platform_url', 'publish_error',
            ])

            account.total_posts_published += 1
            account.last_used_at = timezone.now()
            account.save(update_fields=['total_posts_published', 'last_used_at'])

            logger.info(f"Post retry basarili: {post_id}")
        else:
            post.status = 'failed'
            post.publish_error = result.error
            post.save(update_fields=['status', 'publish_error'])
            logger.warning(f"Post retry basarisiz: {post_id}, error={result.error}")

            # Retry with exponential backoff
            raise self.retry(countdown=60 * (2 ** self.request.retries))

    except self.MaxRetriesExceededError:
        post.status = 'failed'
        post.publish_error = f"Max retry ({self.max_retries}) asildi"
        post.save(update_fields=['status', 'publish_error'])
        logger.error(f"Post max retry asildi: {post_id}")

    except Exception as e:
        logger.exception(f"Post retry hatasi: {post_id}")
        post.status = 'failed'
        post.publish_error = str(e)
        post.save(update_fields=['status', 'publish_error'])

        PublishLog.objects.create(
            post=post,
            action='retry',
            success=False,
            error_message=str(e),
        )

        try:
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        except self.MaxRetriesExceededError:
            post.publish_error = f"Max retry asildi: {str(e)}"
            post.save(update_fields=['publish_error'])
