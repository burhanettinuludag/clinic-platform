from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedModel


class DoctorNote(TimeStampedModel):
    class NoteType(models.TextChoices):
        GENERAL = 'general', 'General'
        FOLLOW_UP = 'follow_up', 'Follow Up'
        MEDICATION_CHANGE = 'medication_change', 'Medication Change'
        ALERT_RESPONSE = 'alert_response', 'Alert Response'

    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_notes',
        limit_choices_to={'role': 'doctor'},
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient_notes',
        limit_choices_to={'role': 'patient'},
    )
    note_type = models.CharField(
        max_length=20,
        choices=NoteType.choices,
        default=NoteType.GENERAL,
    )
    content = models.TextField()
    is_private = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['doctor', 'patient', '-created_at']),
        ]

    def __str__(self):
        return f"Note by Dr. {self.doctor.get_full_name()} for {self.patient.get_full_name()}"
