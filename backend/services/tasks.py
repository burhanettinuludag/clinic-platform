"""
Celery task'lari - Asenkron pipeline calistirma.

Orkestrator.run_pipeline_async() bu task'i tetikler.
"""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=1,
    default_retry_delay=60,
    name='services.run_pipeline_task',
)
def run_pipeline_task(
    self,
    pipeline_name: str,
    input_data: dict,
    steps=None,
    triggered_by_id=None,
):
    """
    Asenkron pipeline calistirma Celery task'i.

    Pipeline tamamlandiginda sonucu Notification olarak kaydeder.
    """
    from services.orchestrator import orchestrator

    # Kullanici objesini al (opsiyonel)
    triggered_by = None
    if triggered_by_id:
        try:
            from apps.accounts.models import CustomUser
            triggered_by = CustomUser.objects.get(id=triggered_by_id)
        except Exception:
            pass

    logger.info(
        f"Async pipeline starting: {pipeline_name}, "
        f"triggered_by={triggered_by_id}"
    )

    try:
        result = orchestrator.run_chain(
            pipeline_name=pipeline_name,
            input_data=input_data,
            steps=steps,
            triggered_by=triggered_by,
        )

        # Sonucu bildirim olarak kaydet
        if triggered_by:
            _create_notification(
                recipient=triggered_by,
                pipeline_name=pipeline_name,
                success=result.success,
                completed=result.steps_completed,
                failed=result.steps_failed,
                error=result.error,
            )

        return {
            'success': result.success,
            'pipeline': pipeline_name,
            'completed': result.steps_completed,
            'failed': result.steps_failed,
            'duration_ms': result.total_duration_ms,
        }

    except Exception as exc:
        logger.exception(f"Pipeline task failed: {pipeline_name}")
        raise self.retry(exc=exc)


def _create_notification(
    recipient, pipeline_name, success, completed, failed, error
):
    """Pipeline sonucunu Notification olarak kaydet."""
    try:
        from apps.notifications.models import Notification

        if success:
            title_tr = f"Islem tamamlandi: {pipeline_name}"
            title_en = f"Task completed: {pipeline_name}"
            message_tr = f"Tamamlanan adimlar: {', '.join(completed)}"
            message_en = f"Completed steps: {', '.join(completed)}"
            ntype = 'info'
        else:
            title_tr = f"Islem basarisiz: {pipeline_name}"
            title_en = f"Task failed: {pipeline_name}"
            message_tr = f"Hata: {error}. Basarisiz: {', '.join(failed)}"
            message_en = f"Error: {error}. Failed: {', '.join(failed)}"
            ntype = 'alert'

        Notification.objects.create(
            recipient=recipient,
            notification_type=ntype,
            title_tr=title_tr,
            title_en=title_en,
            message_tr=message_tr,
            message_en=message_en,
            metadata={
                'pipeline': pipeline_name,
                'completed': completed,
                'failed': failed,
            },
        )
    except Exception as e:
        logger.error(f"Failed to create notification: {e}")
