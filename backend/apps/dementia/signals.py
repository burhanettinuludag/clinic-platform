"""
Dementia app signals.

ExerciseSession kaydedildiginde otomatik skor hesaplama tetikler.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender='dementia.ExerciseSession')
def trigger_score_calculation(sender, instance, created, **kwargs):
    """ExerciseSession olusturulunca o gun icin skor hesapla."""
    if created and instance.started_at:
        from apps.dementia.tasks import calculate_patient_score
        date_str = instance.started_at.strftime('%Y-%m-%d')
        calculate_patient_score.delay(str(instance.patient_id), date_str)
