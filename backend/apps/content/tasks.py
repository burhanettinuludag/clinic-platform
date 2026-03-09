"""
Content app Celery tasks.

- auto_generate_weekly_content: Haftalik otomatik icerik uretimi
- cleanup_old_agent_tasks: Eski AgentTask kayitlarini temizle
- send_weekly_content_report: Haftalik icerik raporu
"""

import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


@shared_task(name='apps.content.tasks.auto_generate_weekly_content')
def auto_generate_weekly_content():
    """
    Haftalik otomatik icerik uretimi.

    SiteConfig'den topic listesini alir (key: 'auto_content_topics'),
    her topic icin 'full_content_v5' pipeline'ini tetikler.
    """
    from apps.common.models import SiteConfig
    from services.orchestrator import orchestrator

    try:
        config = SiteConfig.objects.filter(key='auto_content_topics').first()
    except Exception as e:
        logger.error(f"SiteConfig sorgulanamadi: {e}")
        return {'success': False, 'error': str(e)}

    if not config:
        logger.info("auto_content_topics SiteConfig bulunamadi, atlanıyor")
        return {'success': False, 'error': 'auto_content_topics not configured'}

    topics = config.get_typed_value()
    if not isinstance(topics, list) or not topics:
        logger.warning("auto_content_topics bos veya liste degil")
        return {'success': False, 'error': 'topics is empty or not a list'}

    from apps.content.models import Article
    from django.utils.text import slugify

    results = []
    for topic in topics:
        try:
            result = orchestrator.run_chain(
                pipeline_name='full_content_v5',
                input_data={
                    'topic': topic,
                    'module': 'general',
                    'content_type': 'blog',
                    'audience': 'patient',
                },
            )

            # Basarili ise Article olarak kaydet
            article_id = None
            if result.success and result.final_data:
                data = result.final_data
                title_tr = data.get('title_tr', topic)
                base_slug = slugify(title_tr[:180], allow_unicode=True) or slugify(topic[:180])
                slug = base_slug
                counter = 1
                while Article.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1

                article = Article.objects.create(
                    slug=slug,
                    title_tr=title_tr,
                    title_en=data.get('title_en', ''),
                    body_tr=data.get('body_tr', ''),
                    body_en=data.get('body_en', ''),
                    excerpt_tr=data.get('excerpt_tr', '')[:500],
                    excerpt_en=data.get('excerpt_en', '')[:500],
                    seo_title_tr=data.get('seo_title_tr', '')[:200],
                    seo_title_en=data.get('seo_title_en', '')[:200],
                    seo_description_tr=data.get('seo_description_tr', '')[:500],
                    seo_description_en=data.get('seo_description_en', '')[:500],
                    status='draft',
                )
                article_id = str(article.id)
                logger.info(f"Auto content article saved: '{title_tr}' (id={article_id})")

            results.append({
                'topic': topic,
                'success': result.success,
                'steps_completed': result.steps_completed,
                'steps_failed': result.steps_failed,
                'article_id': article_id,
            })
            logger.info(
                f"Auto content '{topic}': success={result.success}, "
                f"completed={result.steps_completed}"
            )
        except Exception as e:
            logger.error(f"Auto content '{topic}' failed: {e}")
            results.append({'topic': topic, 'success': False, 'error': str(e)})

    succeeded = sum(1 for r in results if r.get('success'))
    return {
        'success': True,
        'total': len(topics),
        'succeeded': succeeded,
        'failed': len(topics) - succeeded,
        'results': results,
    }


@shared_task(name='apps.content.tasks.cleanup_old_agent_tasks')
def cleanup_old_agent_tasks():
    """30 günden eski completed/failed AgentTask kayitlarini sil."""
    from apps.common.models import AgentTask

    cutoff = timezone.now() - timedelta(days=30)
    qs = AgentTask.objects.filter(
        status__in=['completed', 'failed'],
        created_at__lt=cutoff,
    )
    count, _ = qs.delete()
    logger.info(f"Cleaned up {count} old AgentTask records (older than 30 days)")
    return {'deleted': count}


@shared_task(name='apps.content.tasks.send_weekly_content_report')
def send_weekly_content_report():
    """
    Haftalik icerik raporu.

    Son 7 gunde uretilen icerik sayisi, basari/basarisizlik orani,
    toplam token kullanimini admin kullanicilarina notification olarak gonderir.
    """
    from apps.common.models import AgentTask
    from apps.accounts.models import CustomUser
    from apps.notifications.models import Notification
    from django.db.models import Sum, Count, Q

    week_ago = timezone.now() - timedelta(days=7)

    stats = AgentTask.objects.filter(
        created_at__gte=week_ago,
    ).aggregate(
        total=Count('id'),
        completed=Count('id', filter=Q(status='completed')),
        failed=Count('id', filter=Q(status='failed')),
        total_tokens=Sum('tokens_used'),
    )

    total = stats['total'] or 0
    completed = stats['completed'] or 0
    failed = stats['failed'] or 0
    total_tokens = stats['total_tokens'] or 0
    success_rate = round((completed / total) * 100, 1) if total > 0 else 0

    message_tr = (
        f"Son 7 gun icerik raporu:\n"
        f"- Toplam gorev: {total}\n"
        f"- Basarili: {completed}\n"
        f"- Basarisiz: {failed}\n"
        f"- Basari orani: %{success_rate}\n"
        f"- Toplam token: {total_tokens:,}"
    )
    message_en = (
        f"Weekly content report:\n"
        f"- Total tasks: {total}\n"
        f"- Completed: {completed}\n"
        f"- Failed: {failed}\n"
        f"- Success rate: {success_rate}%\n"
        f"- Total tokens: {total_tokens:,}"
    )

    admins = CustomUser.objects.filter(is_superuser=True, is_active=True)
    created = 0
    for admin in admins:
        try:
            Notification.objects.create(
                recipient=admin,
                notification_type='system',
                title_tr='Haftalik Icerik Raporu',
                title_en='Weekly Content Report',
                message_tr=message_tr,
                message_en=message_en,
                metadata={
                    'total': total,
                    'completed': completed,
                    'failed': failed,
                    'success_rate': success_rate,
                    'total_tokens': total_tokens,
                },
            )
            created += 1
        except Exception as e:
            logger.error(f"Notification gonderilemedi (admin={admin.id}): {e}")

    logger.info(f"Weekly content report sent to {created} admins")
    return {
        'admins_notified': created,
        'total_tasks': total,
        'completed': completed,
        'failed': failed,
        'success_rate': success_rate,
        'total_tokens': total_tokens,
    }
