"""
Dementia app Celery tasks.

- calculate_daily_cognitive_scores: Gunluk bilissel puan hesapla (onceki gun)
- calculate_patient_score: Tek hasta icin skor hesapla (signal'den tetiklenir)
"""

import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

logger = logging.getLogger(__name__)

# ExerciseType -> CognitiveScore field mapping
EXERCISE_TYPE_TO_SCORE_FIELD = {
    'memory': 'memory_score',
    'attention': 'attention_score',
    'language': 'language_score',
    'problem_solving': 'problem_solving_score',
    'orientation': 'orientation_score',
    'calculation': 'problem_solving_score',  # calculation -> problem_solving
}


def _calculate_for_patient(patient_id, target_date):
    """
    Core logic: Tek hasta + tek gun icin CognitiveScore hesapla ve kaydet.
    """
    from apps.dementia.models import ExerciseSession, CognitiveScore
    from django.db.models import Avg, Count, Sum

    sessions = ExerciseSession.objects.filter(
        patient_id=patient_id,
        started_at__date=target_date,
    ).select_related('exercise')

    if not sessions.exists():
        return

    # exercise_type bazinda avg accuracy
    type_scores = (
        sessions
        .values('exercise__exercise_type')
        .annotate(avg_accuracy=Avg('accuracy_percent'))
    )

    # Domain score field'larina map et
    domain_values = {}
    for ts in type_scores:
        exercise_type = ts['exercise__exercise_type']
        field_name = EXERCISE_TYPE_TO_SCORE_FIELD.get(exercise_type)
        if field_name and ts['avg_accuracy'] is not None:
            new_val = Decimal(str(ts['avg_accuracy']))
            if field_name in domain_values:
                # Birden fazla type ayni field'a map ediyorsa ortalama al
                domain_values[field_name] = (domain_values[field_name] + new_val) / 2
            else:
                domain_values[field_name] = new_val

    # Overall: non-null domain skorlarinin ortalamasi
    valid_scores = [v for v in domain_values.values() if v is not None]
    overall = sum(valid_scores) / len(valid_scores) if valid_scores else None

    # Toplam egzersiz ve sure
    agg = sessions.aggregate(
        count=Count('id'),
        total_seconds=Sum('duration_seconds'),
    )
    total_minutes = (agg['total_seconds'] or 0) // 60

    CognitiveScore.objects.update_or_create(
        patient_id=patient_id,
        score_date=target_date,
        defaults={
            **domain_values,
            'overall_score': overall,
            'exercises_completed': agg['count'] or 0,
            'total_exercise_minutes': total_minutes,
        },
    )


@shared_task(name='apps.dementia.tasks.calculate_daily_cognitive_scores')
def calculate_daily_cognitive_scores(target_date_str=None):
    """
    Gunluk bilissel puan hesapla.

    Varsayilan: onceki gun. Celery Beat ile her gun 01:30'da calisir.
    Manuel: calculate_daily_cognitive_scores('2026-03-07')
    """
    from apps.dementia.models import ExerciseSession
    from datetime import datetime

    if target_date_str:
        target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
    else:
        target_date = (timezone.now() - timedelta(days=1)).date()

    try:
        patient_ids = (
            ExerciseSession.objects
            .filter(started_at__date=target_date)
            .values_list('patient_id', flat=True)
            .distinct()
        )

        processed = 0
        errors = 0

        for patient_id in patient_ids:
            try:
                _calculate_for_patient(patient_id, target_date)
                processed += 1
            except Exception as e:
                logger.error(f"Skor hesaplama hatasi (patient={patient_id}): {e}")
                errors += 1

        logger.info(
            f"Gunluk bilissel skorlar hesaplandi (tarih={target_date}): "
            f"basarili={processed}, hata={errors}"
        )
        return {
            'success': True,
            'date': str(target_date),
            'processed': processed,
            'errors': errors,
        }

    except Exception as e:
        logger.error(f"calculate_daily_cognitive_scores basarisiz: {e}")
        return {'success': False, 'error': str(e)}


@shared_task(name='apps.dementia.tasks.calculate_patient_score')
def calculate_patient_score(patient_id, date_str):
    """
    Tek hasta icin bilissel skor hesapla.
    ExerciseSession post_save signal'i tarafindan tetiklenir.
    """
    from datetime import datetime

    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        _calculate_for_patient(patient_id, target_date)
        logger.info(f"Hasta skoru hesaplandi: patient={patient_id}, date={date_str}")
        return {'success': True, 'patient_id': str(patient_id), 'date': date_str}
    except Exception as e:
        logger.error(f"calculate_patient_score basarisiz: {e}")
        return {'success': False, 'error': str(e)}


@shared_task(name='apps.dementia.tasks.send_dementia_exercise_reminders')
def send_dementia_exercise_reminders():
    """
    Bugun egzersiz yapmayan demans hastalarini hatirla.
    Celery Beat: her gun 19:00.
    """
    from django.contrib.auth import get_user_model
    from apps.dementia.models import ExerciseSession
    from apps.dementia.notifications import notify_exercise_reminder

    User = get_user_model()
    today = timezone.now().date()

    try:
        # Demans modulu aktif olan hastalar (en az 1 exercise session'i olan)
        dementia_patients = (
            User.objects.filter(role='patient')
            .filter(exercise_sessions__isnull=False)
            .distinct()
        )

        # Bugun egzersiz yapanlar
        exercised_today = set(
            ExerciseSession.objects.filter(started_at__date=today)
            .values_list('patient_id', flat=True)
            .distinct()
        )

        sent = 0
        for patient in dementia_patients:
            if patient.id not in exercised_today:
                try:
                    notify_exercise_reminder(patient)
                    sent += 1
                except Exception as e:
                    logger.warning(f"Egzersiz hatirlatma gonderilemedi ({patient.email}): {e}")

        logger.info(f"Demans egzersiz hatirlatmalari gonderildi: {sent} hasta")
        return {'success': True, 'sent': sent}

    except Exception as e:
        logger.error(f"send_dementia_exercise_reminders basarisiz: {e}")
        return {'success': False, 'error': str(e)}


@shared_task(name='apps.dementia.tasks.check_cognitive_score_trends')
def check_cognitive_score_trends():
    """
    Bilissel skor dususu kontrol et.
    Son 7 gunluk ortalama vs onceki 7 gunluk ortalama karsilastirir.
    Dusus %15'ten fazla ise bildirim gonderir.
    Celery Beat: her gun 02:00.
    """
    from apps.dementia.models import CognitiveScore
    from apps.dementia.notifications import notify_score_decline
    from django.db.models import Avg

    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    two_weeks_ago = today - timedelta(days=14)

    try:
        # Son 2 haftada skoru olan hastalari bul
        patient_ids = (
            CognitiveScore.objects.filter(score_date__gte=two_weeks_ago)
            .values_list('patient_id', flat=True)
            .distinct()
        )

        alerts_sent = 0
        for patient_id in patient_ids:
            try:
                # Onceki hafta ortalama
                prev_avg = CognitiveScore.objects.filter(
                    patient_id=patient_id,
                    score_date__gte=two_weeks_ago,
                    score_date__lt=week_ago,
                    overall_score__isnull=False,
                ).aggregate(avg=Avg('overall_score'))['avg']

                # Son hafta ortalama
                curr_avg = CognitiveScore.objects.filter(
                    patient_id=patient_id,
                    score_date__gte=week_ago,
                    overall_score__isnull=False,
                ).aggregate(avg=Avg('overall_score'))['avg']

                if prev_avg and curr_avg and prev_avg > 0:
                    decline_pct = (float(prev_avg) - float(curr_avg)) / float(prev_avg) * 100
                    if decline_pct >= 15:
                        from django.contrib.auth import get_user_model
                        User = get_user_model()
                        patient = User.objects.get(id=patient_id)
                        notify_score_decline(patient, float(prev_avg), float(curr_avg))
                        alerts_sent += 1
                        logger.info(
                            f"Skor dususu bildirimi: patient={patient_id}, "
                            f"onceki={prev_avg:.1f}, simdi={curr_avg:.1f}, dusus={decline_pct:.1f}%"
                        )

            except Exception as e:
                logger.warning(f"Skor trend kontrolu hatasi (patient={patient_id}): {e}")

        logger.info(f"Bilissel skor trend kontrolu tamamlandi: {alerts_sent} uyari gonderildi")
        return {'success': True, 'alerts_sent': alerts_sent}

    except Exception as e:
        logger.error(f"check_cognitive_score_trends basarisiz: {e}")
        return {'success': False, 'error': str(e)}
