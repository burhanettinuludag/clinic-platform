from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedModel


class DiseaseModule(TimeStampedModel):
    class DiseaseType(models.TextChoices):
        MIGRAINE = 'migraine', 'Migraine'
        EPILEPSY = 'epilepsy', 'Epilepsy'
        PARKINSON = 'parkinson', 'Parkinson'
        DEMENTIA = 'dementia', 'Dementia'

    slug = models.SlugField(unique=True)
    disease_type = models.CharField(max_length=20, choices=DiseaseType.choices, unique=True)
    name_tr = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    description_tr = models.TextField(blank=True, default='')
    description_en = models.TextField(blank=True, default='')
    icon = models.CharField(max_length=50, blank=True, default='')
    is_active = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name_en


class PatientModule(TimeStampedModel):
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrolled_modules',
        limit_choices_to={'role': 'patient'},
    )
    disease_module = models.ForeignKey(
        DiseaseModule,
        on_delete=models.CASCADE,
        related_name='enrolled_patients',
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['patient', 'disease_module']

    def __str__(self):
        return f"{self.patient} - {self.disease_module}"


class TaskTemplate(TimeStampedModel):
    class TaskFrequency(models.TextChoices):
        DAILY = 'daily', 'Daily'
        WEEKLY = 'weekly', 'Weekly'
        ON_EVENT = 'on_event', 'On Event'
        ONE_TIME = 'one_time', 'One Time'

    class TaskType(models.TextChoices):
        DIARY_ENTRY = 'diary_entry', 'Diary Entry'
        CHECKLIST = 'checklist', 'Checklist'
        EDUCATION = 'education', 'Education'
        EXERCISE = 'exercise', 'Exercise'
        MEDICATION = 'medication', 'Medication'
        SURVEY = 'survey', 'Survey'

    disease_module = models.ForeignKey(
        DiseaseModule,
        on_delete=models.CASCADE,
        related_name='task_templates',
    )
    title_tr = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200)
    description_tr = models.TextField(blank=True, default='')
    description_en = models.TextField(blank=True, default='')
    task_type = models.CharField(max_length=20, choices=TaskType.choices)
    frequency = models.CharField(max_length=20, choices=TaskFrequency.choices)
    points = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['disease_module', 'order']

    def __str__(self):
        return self.title_en


class TaskCompletion(TimeStampedModel):
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='task_completions',
    )
    task_template = models.ForeignKey(
        TaskTemplate,
        on_delete=models.CASCADE,
        related_name='completions',
    )
    completed_date = models.DateField()
    response_data = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True, default='')

    class Meta:
        indexes = [
            models.Index(fields=['patient', '-completed_date']),
            models.Index(fields=['task_template', 'patient']),
        ]

    def __str__(self):
        return f"{self.patient} completed {self.task_template} on {self.completed_date}"
