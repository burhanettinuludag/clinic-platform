"""
Varsayilan periyodik gorevleri django_celery_beat ile olusturur.

Kullanim:
    python manage.py setup_periodic_tasks
"""

from django.core.management.base import BaseCommand
from django_celery_beat.models import CrontabSchedule, PeriodicTask


class Command(BaseCommand):
    help = 'Varsayilan periyodik gorevleri olusturur (django_celery_beat)'

    TASKS = [
        {
            'name': 'Auto Generate Weekly Content',
            'task': 'apps.content.tasks.auto_generate_weekly_content',
            'crontab': {'minute': '0', 'hour': '9', 'day_of_week': '1'},  # Pazartesi 09:00
            'description': 'Haftalik otomatik icerik uretimi',
        },
        {
            'name': 'Cleanup Old Agent Tasks',
            'task': 'apps.content.tasks.cleanup_old_agent_tasks',
            'crontab': {'minute': '0', 'hour': '3'},  # Her gun 03:00
            'description': 'Eski AgentTask kayitlarini temizle (30 gun)',
        },
        {
            'name': 'Send Weekly Content Report',
            'task': 'apps.content.tasks.send_weekly_content_report',
            'crontab': {'minute': '0', 'hour': '17', 'day_of_week': '5'},  # Cuma 17:00
            'description': 'Haftalik icerik raporu admin kullanicilara',
        },
        {
            'name': 'Calculate Daily Cognitive Scores',
            'task': 'apps.dementia.tasks.calculate_daily_cognitive_scores',
            'crontab': {'minute': '30', 'hour': '1'},  # Her gun 01:30
            'description': 'Gunluk bilissel skor hesaplama (onceki gun)',
        },
        {
            'name': 'Send Dementia Exercise Reminders',
            'task': 'apps.dementia.tasks.send_dementia_exercise_reminders',
            'crontab': {'minute': '0', 'hour': '19'},  # Her gun 19:00
            'description': 'Bugun egzersiz yapmayan demans hastalarina hatirlatma',
        },
        {
            'name': 'Check Cognitive Score Trends',
            'task': 'apps.dementia.tasks.check_cognitive_score_trends',
            'crontab': {'minute': '0', 'hour': '2'},  # Her gun 02:00
            'description': 'Bilissel skor dususu kontrol ve bildirim',
        },
    ]

    def handle(self, *args, **options):
        created_count = 0

        for task_def in self.TASKS:
            cron_kwargs = {
                'minute': task_def['crontab'].get('minute', '0'),
                'hour': task_def['crontab'].get('hour', '0'),
                'day_of_week': task_def['crontab'].get('day_of_week', '*'),
                'day_of_month': task_def['crontab'].get('day_of_month', '*'),
                'month_of_year': task_def['crontab'].get('month_of_year', '*'),
            }

            schedule, _ = CrontabSchedule.objects.get_or_create(
                **cron_kwargs,
                defaults={'timezone': 'Europe/Istanbul'},
            )

            _, created = PeriodicTask.objects.update_or_create(
                name=task_def['name'],
                defaults={
                    'task': task_def['task'],
                    'crontab': schedule,
                    'enabled': True,
                    'description': task_def['description'],
                },
            )

            status = 'CREATED' if created else 'UPDATED'
            created_count += 1 if created else 0
            self.stdout.write(f"  [{status}] {task_def['name']} -> {task_def['task']}")

        self.stdout.write(self.style.SUCCESS(
            f"\n{created_count} yeni gorev olusturuldu, "
            f"{len(self.TASKS) - created_count} gorev guncellendi."
        ))
