from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedModel


class MigraineTrigger(TimeStampedModel):
    class TriggerCategory(models.TextChoices):
        DIETARY = 'dietary', 'Dietary'
        ENVIRONMENTAL = 'environmental', 'Environmental'
        HORMONAL = 'hormonal', 'Hormonal'
        EMOTIONAL = 'emotional', 'Emotional'
        PHYSICAL = 'physical', 'Physical'
        SLEEP = 'sleep', 'Sleep'
        OTHER = 'other', 'Other'

    name_tr = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=TriggerCategory.choices)
    is_predefined = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='custom_triggers',
    )

    class Meta:
        ordering = ['category', 'name_en']

    def __str__(self):
        return self.name_en


class MigraineAttack(TimeStampedModel):
    class PainLocation(models.TextChoices):
        LEFT = 'left', 'Left'
        RIGHT = 'right', 'Right'
        BILATERAL = 'bilateral', 'Bilateral'
        FRONTAL = 'frontal', 'Frontal'
        OCCIPITAL = 'occipital', 'Occipital'
        OTHER = 'other', 'Other'

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='migraine_attacks',
    )
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    intensity = models.PositiveSmallIntegerField(
        help_text="Pain intensity 1-10"
    )
    pain_location = models.CharField(
        max_length=20,
        choices=PainLocation.choices,
        blank=True,
        default='',
    )
    has_aura = models.BooleanField(default=False)
    has_nausea = models.BooleanField(default=False)
    has_vomiting = models.BooleanField(default=False)
    has_photophobia = models.BooleanField(default=False)
    has_phonophobia = models.BooleanField(default=False)
    medication_taken = models.CharField(max_length=200, blank=True, default='')
    medication_effective = models.BooleanField(null=True, blank=True)
    triggers_identified = models.ManyToManyField(
        MigraineTrigger,
        blank=True,
        related_name='attacks',
    )
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-start_datetime']
        indexes = [
            models.Index(fields=['patient', '-start_datetime']),
        ]

    def __str__(self):
        return f"Attack on {self.start_datetime.date()} - Intensity: {self.intensity}"
