"""
Agent Yonetim Paneli API'leri.
Sadece superuser Celery task'lari tetikleyebilir.
Cooldown, gunluk limit ve audit log ile korunur.
"""

import logging
from datetime import timedelta

from rest_framework import serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Count, Q, Sum

from apps.accounts.permissions import IsAdminUser
from apps.common.models import AgentTask, AuditLog

logger = logging.getLogger(__name__)

# ==================== TASK REGISTRY ====================
# Her task icin metadata: ad, aciklama, kategori, tehlike seviyesi, cooldown

TASK_REGISTRY = {
    'auto_generate_weekly_content': {
        'task_path': 'apps.content.tasks.auto_generate_weekly_content',
        'name_tr': 'Haftalik Icerik Uretimi',
        'name_en': 'Weekly Content Generation',
        'description_tr': 'SiteConfig deki tum topiclerde blog yazisi uretir (AI). Uretilen icerikler "taslak" olarak kaydedilir.',
        'description_en': 'Generates blog posts for all topics in SiteConfig (AI). Generated content is saved as "draft".',
        'category': 'content',
        'risk_level': 'high',  # AI kredi tuketir
        'cooldown_minutes': 120,  # 2 saat
        'schedule_info': 'Pazartesi 09:00',
    },
    'send_weekly_content_report': {
        'task_path': 'apps.content.tasks.send_weekly_content_report',
        'name_tr': 'Haftalik Icerik Raporu',
        'name_en': 'Weekly Content Report',
        'description_tr': 'Son 7 gunun icerik istatistiklerini admin bildirim olarak gonderir.',
        'description_en': 'Sends last 7 days content statistics as admin notification.',
        'category': 'report',
        'risk_level': 'low',
        'cooldown_minutes': 30,
        'schedule_info': 'Cuma 17:00',
    },
    'send_daily_education_drip': {
        'task_path': 'apps.content.tasks.send_daily_education_drip',
        'name_tr': 'Gunluk Egitim Bildirimi',
        'name_en': 'Daily Education Drip',
        'description_tr': 'Migren modulune kayitli hastalara siradaki egitim kartini bildirim olarak gonderir.',
        'description_en': 'Sends next education card as notification to migraine module patients.',
        'category': 'notification',
        'risk_level': 'medium',
        'cooldown_minutes': 60,
        'schedule_info': 'Her gun 09:00',
    },
    'cleanup_old_agent_tasks': {
        'task_path': 'apps.content.tasks.cleanup_old_agent_tasks',
        'name_tr': 'Eski Agent Kayitlarini Temizle',
        'name_en': 'Cleanup Old Agent Tasks',
        'description_tr': '30 gunden eski tamamlanmis/basarisiz AgentTask kayitlarini siler.',
        'description_en': 'Deletes completed/failed AgentTask records older than 30 days.',
        'category': 'maintenance',
        'risk_level': 'low',
        'cooldown_minutes': 60,
        'schedule_info': 'Her gun 03:00',
    },
    'cleanup_old_notifications': {
        'task_path': 'apps.notifications.tasks.cleanup_old_notifications',
        'name_tr': 'Eski Bildirimleri Temizle',
        'name_en': 'Cleanup Old Notifications',
        'description_tr': 'Eski bildirimleri temizler.',
        'description_en': 'Cleans up old notifications.',
        'category': 'maintenance',
        'risk_level': 'low',
        'cooldown_minutes': 60,
        'schedule_info': 'Her gun 03:00',
    },
    'daily_streak_check': {
        'task_path': 'apps.gamification.tasks.daily_streak_check',
        'name_tr': 'Gunluk Streak Kontrolu',
        'name_en': 'Daily Streak Check',
        'description_tr': 'Kullanici streak lerini kontrol eder ve gunceller.',
        'description_en': 'Checks and updates user streaks.',
        'category': 'gamification',
        'risk_level': 'low',
        'cooldown_minutes': 30,
        'schedule_info': 'Her gun 00:30',
    },
    'scan_broken_links': {
        'task_path': 'apps.common.tasks.scan_broken_links',
        'name_tr': 'Kirik Link Taramasi',
        'name_en': 'Broken Link Scan',
        'description_tr': 'Tum iceriklerdeki linkleri tarar, kirik olanlari tespit eder ve mumkunse otomatik tamir eder.',
        'description_en': 'Scans all content links, detects broken ones, and auto-fixes when possible.',
        'category': 'maintenance',
        'risk_level': 'medium',
        'cooldown_minutes': 120,
        'schedule_info': 'Carsamba 04:00',
    },
    'send_medication_reminders': {
        'task_path': 'apps.tracking.tasks.send_medication_reminders',
        'name_tr': 'Ilac Hatirlatmalari',
        'name_en': 'Medication Reminders',
        'description_tr': 'Zamani gelen ilac hatirlatmalarini gonderir.',
        'description_en': 'Sends medication reminders that are due.',
        'category': 'notification',
        'risk_level': 'low',
        'cooldown_minutes': 15,
        'schedule_info': 'Her 15 dakika',
    },
    'update_weather_cache': {
        'task_path': 'apps.wellness.tasks.update_weather_cache',
        'name_tr': 'Hava Durumu Guncelle',
        'name_en': 'Update Weather Cache',
        'description_tr': 'Hava durumu onbellegini gunceller.',
        'description_en': 'Updates weather cache.',
        'category': 'maintenance',
        'risk_level': 'low',
        'cooldown_minutes': 60,
        'schedule_info': 'Her 3 saat',
    },
    'calculate_daily_cognitive_scores': {
        'task_path': 'apps.dementia.tasks.calculate_daily_cognitive_scores',
        'name_tr': 'Bilissel Skor Hesapla',
        'name_en': 'Calculate Cognitive Scores',
        'description_tr': 'Demans hastalari icin gunluk bilissel skor hesaplar.',
        'description_en': 'Calculates daily cognitive scores for dementia patients.',
        'category': 'analysis',
        'risk_level': 'low',
        'cooldown_minutes': 60,
        'schedule_info': 'Manuel',
    },
    'publish_scheduled_posts': {
        'task_path': 'apps.social.tasks.publish_scheduled_posts',
        'name_tr': 'Planli Sosyal Medya Paylasimlarini Yayinla',
        'name_en': 'Publish Scheduled Social Posts',
        'description_tr': 'Zamani gelen sosyal medya paylasimlarin yayinlar.',
        'description_en': 'Publishes scheduled social media posts that are due.',
        'category': 'social',
        'risk_level': 'medium',
        'cooldown_minutes': 5,
        'schedule_info': 'Her 5 dakika',
    },
}

# Gunluk max tetikleme limiti
DAILY_TRIGGER_LIMIT = 10

# ==================== SERIALIZERS ====================

class TriggerTaskSerializer(serializers.Serializer):
    task_key = serializers.ChoiceField(choices=list(TASK_REGISTRY.keys()))


# ==================== VIEWS ====================

class AgentListView(APIView):
    """
    Tum tetiklenebilir agent/task listesini dondurur.
    Her biri icin son calisma bilgisi ve cooldown durumu dahil.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        # Sadece superuser erisebilir
        if not request.user.is_superuser:
            return Response(
                {'error': 'Bu isleme sadece superuser erisebilir.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Bugunun tetikleme sayisi
        today_triggers = AuditLog.objects.filter(
            action='agent_trigger',
            created_at__gte=today_start,
        ).count()

        agents = []
        for key, meta in TASK_REGISTRY.items():
            # Son basarili calisma
            last_task = AgentTask.objects.filter(
                task_type=key,
            ).order_by('-created_at').first()

            # Son tetikleme zamani (cooldown kontrolu icin)
            last_trigger = AuditLog.objects.filter(
                action='agent_trigger',
                details__task_key=key,
            ).order_by('-created_at').first()

            cooldown_remaining = 0
            if last_trigger:
                cooldown_end = last_trigger.created_at + timedelta(minutes=meta['cooldown_minutes'])
                if now < cooldown_end:
                    cooldown_remaining = int((cooldown_end - now).total_seconds())

            agents.append({
                'key': key,
                'name_tr': meta['name_tr'],
                'name_en': meta['name_en'],
                'description_tr': meta['description_tr'],
                'description_en': meta['description_en'],
                'category': meta['category'],
                'risk_level': meta['risk_level'],
                'cooldown_minutes': meta['cooldown_minutes'],
                'cooldown_remaining_seconds': cooldown_remaining,
                'schedule_info': meta['schedule_info'],
                'last_run': {
                    'status': last_task.status if last_task else None,
                    'created_at': last_task.created_at.isoformat() if last_task else None,
                    'duration_ms': last_task.duration_ms if last_task else None,
                    'tokens_used': last_task.tokens_used if last_task else None,
                } if last_task else None,
            })

        return Response({
            'agents': agents,
            'daily_triggers_used': today_triggers,
            'daily_trigger_limit': DAILY_TRIGGER_LIMIT,
        })


class TriggerAgentView(APIView):
    """
    Bir agent/task'i elle tetikler.
    Guvenlik katmanlari:
    1. Sadece superuser
    2. Cooldown kontrolu
    3. Gunluk limit
    4. AuditLog kaydı
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        # 1. Superuser kontrolu
        if not request.user.is_superuser:
            return Response(
                {'error': 'Bu isleme sadece superuser erisebilir.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = TriggerTaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task_key = serializer.validated_data['task_key']
        meta = TASK_REGISTRY[task_key]

        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # 2. Gunluk limit kontrolu
        today_triggers = AuditLog.objects.filter(
            action='agent_trigger',
            created_at__gte=today_start,
        ).count()

        if today_triggers >= DAILY_TRIGGER_LIMIT:
            return Response({
                'error': f'Gunluk tetikleme limiti ({DAILY_TRIGGER_LIMIT}) asildi. Yarin tekrar deneyin.',
                'daily_triggers_used': today_triggers,
                'daily_trigger_limit': DAILY_TRIGGER_LIMIT,
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # 3. Cooldown kontrolu
        last_trigger = AuditLog.objects.filter(
            action='agent_trigger',
            details__task_key=task_key,
        ).order_by('-created_at').first()

        if last_trigger:
            cooldown_end = last_trigger.created_at + timedelta(minutes=meta['cooldown_minutes'])
            if now < cooldown_end:
                remaining = int((cooldown_end - now).total_seconds())
                return Response({
                    'error': f'Cooldown suresi aktif. {remaining} saniye sonra tekrar deneyin.',
                    'cooldown_remaining_seconds': remaining,
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # 4. Task'i tetikle
        try:
            from celery import current_app
            task = current_app.send_task(meta['task_path'])
        except Exception as e:
            logger.error(f"Agent trigger failed: {task_key} - {e}")
            return Response({
                'error': f'Task tetiklenemedi: {str(e)}',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 5. Audit log kaydi
        def get_client_ip():
            x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded:
                return x_forwarded.split(',')[0].strip()
            return request.META.get('REMOTE_ADDR')

        AuditLog.objects.create(
            user=request.user,
            action='agent_trigger',
            resource_type='celery_task',
            ip_address=get_client_ip(),
            details={
                'task_key': task_key,
                'task_path': meta['task_path'],
                'celery_task_id': str(task.id),
                'risk_level': meta['risk_level'],
            },
        )

        logger.info(
            f"Agent triggered: {task_key} by user={request.user.email} "
            f"ip={get_client_ip()} task_id={task.id}"
        )

        return Response({
            'message': f'{meta["name_tr"]} basariyla tetiklendi.',
            'task_key': task_key,
            'celery_task_id': str(task.id),
            'daily_triggers_used': today_triggers + 1,
            'daily_trigger_limit': DAILY_TRIGGER_LIMIT,
        }, status=status.HTTP_202_ACCEPTED)


class AgentTriggerHistoryView(APIView):
    """Son tetikleme gecmisini gosterir."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        if not request.user.is_superuser:
            return Response(
                {'error': 'Bu isleme sadece superuser erisebilir.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        logs = AuditLog.objects.filter(
            action='agent_trigger',
        ).select_related('user').order_by('-created_at')[:50]

        history = []
        for log in logs:
            task_key = log.details.get('task_key', '')
            meta = TASK_REGISTRY.get(task_key, {})
            history.append({
                'id': str(log.id),
                'task_key': task_key,
                'task_name': meta.get('name_tr', task_key),
                'user_email': log.user.email if log.user else 'N/A',
                'ip_address': log.ip_address,
                'celery_task_id': log.details.get('celery_task_id', ''),
                'created_at': log.created_at.isoformat(),
            })

        return Response({'history': history})


class AgentStatsView(APIView):
    """Agent istatistikleri."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        if not request.user.is_superuser:
            return Response(
                {'error': 'Bu isleme sadece superuser erisebilir.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        week_ago = timezone.now() - timedelta(days=7)

        # Haftalik AgentTask istatistikleri
        weekly_stats = AgentTask.objects.filter(
            created_at__gte=week_ago,
        ).aggregate(
            total=Count('id'),
            completed=Count('id', filter=Q(status='completed')),
            failed=Count('id', filter=Q(status='failed')),
            running=Count('id', filter=Q(status='running')),
            total_tokens=Sum('tokens_used'),
        )

        # Task bazli dagilim
        by_task = (
            AgentTask.objects.filter(created_at__gte=week_ago)
            .values('task_type')
            .annotate(
                count=Count('id'),
                success=Count('id', filter=Q(status='completed')),
                fail=Count('id', filter=Q(status='failed')),
                tokens=Sum('tokens_used'),
            )
            .order_by('-count')
        )

        return Response({
            'weekly': {
                'total': weekly_stats['total'] or 0,
                'completed': weekly_stats['completed'] or 0,
                'failed': weekly_stats['failed'] or 0,
                'running': weekly_stats['running'] or 0,
                'total_tokens': weekly_stats['total_tokens'] or 0,
            },
            'by_task': list(by_task),
        })
