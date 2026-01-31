from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedModel


class SymptomDefinition(TimeStampedModel):
    class InputType(models.TextChoices):
        SLIDER = 'slider', 'Slider (0-10)'
        BOOLEAN = 'boolean', 'Yes/No'
        CHOICE = 'choice', 'Multiple Choice'
        TEXT = 'text', 'Free Text'
        NUMBER = 'number', 'Numeric'

    disease_module = models.ForeignKey(
        'patients.DiseaseModule',
        on_delete=models.CASCADE,
        related_name='symptom_definitions',
    )
    key = models.SlugField(max_length=50)
    label_tr = models.CharField(max_length=150)
    label_en = models.CharField(max_length=150)
    input_type = models.CharField(max_length=20, choices=InputType.choices)
    config = models.JSONField(default=dict, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['disease_module', 'key']
        ordering = ['disease_module', 'order']

    def __str__(self):
        return f"{self.disease_module} - {self.label_en}"


class SymptomEntry(TimeStampedModel):
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='symptom_entries',
    )
    symptom_definition = models.ForeignKey(
        SymptomDefinition,
        on_delete=models.CASCADE,
        related_name='entries',
    )
    recorded_date = models.DateField()
    value = models.JSONField()
    notes = models.TextField(blank=True, default='')

    class Meta:
        indexes = [
            models.Index(fields=['patient', '-recorded_date']),
            models.Index(fields=['symptom_definition', 'patient']),
        ]
        unique_together = ['patient', 'symptom_definition', 'recorded_date']

    def __str__(self):
        return f"{self.patient} - {self.symptom_definition.key}: {self.value}"


class Medication(TimeStampedModel):
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='medications',
    )
    name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100, blank=True, default='')
    frequency = models.CharField(max_length=100, blank=True, default='')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.name} ({self.dosage})"


class MedicationLog(TimeStampedModel):
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='medication_logs',
    )
    medication = models.ForeignKey(
        Medication,
        on_delete=models.CASCADE,
        related_name='logs',
    )
    taken_at = models.DateTimeField()
    was_taken = models.BooleanField(default=True)
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-taken_at']

    def __str__(self):
        status = 'taken' if self.was_taken else 'missed'
        return f"{self.medication.name} - {status} at {self.taken_at}"


class ReminderConfig(TimeStampedModel):
    class ReminderType(models.TextChoices):
        MEDICATION = 'medication', 'Medication'
        EXERCISE = 'exercise', 'Exercise'
        SLEEP = 'sleep', 'Sleep Log'
        DIARY = 'diary', 'Diary Entry'
        GENERAL = 'general', 'General'

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reminder_configs',
    )
    reminder_type = models.CharField(max_length=20, choices=ReminderType.choices)
    title = models.CharField(max_length=200)
    time_of_day = models.TimeField()
    days_of_week = models.JSONField(default=list)
    is_enabled = models.BooleanField(default=True)
    linked_medication = models.ForeignKey(
        Medication,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reminders',
    )

    def __str__(self):
        return f"{self.title} - {self.time_of_day}"
