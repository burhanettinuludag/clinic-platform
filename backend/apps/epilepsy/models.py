from django.conf import settings
from django.db import models
from apps.common.models import TimeStampedModel


class EpilepsyTrigger(TimeStampedModel):
    class TriggerCategory(models.TextChoices):
        SLEEP = 'sleep', 'Sleep'
        STRESS = 'stress', 'Stress'
        SUBSTANCE = 'substance', 'Substance'
        SENSORY = 'sensory', 'Sensory'
        PHYSICAL = 'physical', 'Physical'
        HORMONAL = 'hormonal', 'Hormonal'
        OTHER = 'other', 'Other'

    name_tr = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=TriggerCategory.choices, default=TriggerCategory.OTHER)
    is_predefined = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='custom_epilepsy_triggers',
    )

    class Meta:
        ordering = ['category', 'name_en']

    def __str__(self):
        return self.name_en


class SeizureEvent(TimeStampedModel):
    class SeizureType(models.TextChoices):
        FOCAL_AWARE = 'focal_aware', 'Focal Aware'
        FOCAL_IMPAIRED = 'focal_impaired', 'Focal Impaired Awareness'
        GENERALIZED_TONIC_CLONIC = 'generalized_tonic_clonic', 'Generalized Tonic-Clonic'
        GENERALIZED_ABSENCE = 'generalized_absence', 'Absence'
        GENERALIZED_MYOCLONIC = 'generalized_myoclonic', 'Myoclonic'
        UNKNOWN = 'unknown', 'Unknown'

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='seizure_events',
    )
    seizure_datetime = models.DateTimeField()
    seizure_type = models.CharField(max_length=30, choices=SeizureType.choices, default=SeizureType.UNKNOWN)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    intensity = models.PositiveSmallIntegerField(help_text='1-10 scale')
    triggers_identified = models.ManyToManyField(
        EpilepsyTrigger,
        blank=True,
        related_name='seizure_events',
    )
    loss_of_consciousness = models.BooleanField(default=False)
    medication_taken = models.BooleanField(default=True)
    post_ictal_notes = models.TextField(blank=True, default='')
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-seizure_datetime']
        indexes = [
            models.Index(fields=['patient', '-seizure_datetime']),
        ]

    def __str__(self):
        return f"{self.patient} - {self.get_seizure_type_display()} ({self.seizure_datetime})"
