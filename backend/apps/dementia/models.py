"""
Dementia module models for cognitive exercises, daily tracking, and caregiver feedback.
"""
from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedModel


class CognitiveExercise(TimeStampedModel):
    """
    Definition of a cognitive exercise/game.
    """
    class ExerciseType(models.TextChoices):
        MEMORY = 'memory', 'Memory Game'
        ATTENTION = 'attention', 'Attention Test'
        LANGUAGE = 'language', 'Language Exercise'
        PROBLEM_SOLVING = 'problem_solving', 'Problem Solving'
        ORIENTATION = 'orientation', 'Orientation'
        CALCULATION = 'calculation', 'Calculation'

    class DifficultyLevel(models.TextChoices):
        EASY = 'easy', 'Easy'
        MEDIUM = 'medium', 'Medium'
        HARD = 'hard', 'Hard'

    slug = models.SlugField(unique=True, max_length=100)
    name_tr = models.CharField(max_length=200)
    name_en = models.CharField(max_length=200)
    description_tr = models.TextField(blank=True, default='')
    description_en = models.TextField(blank=True, default='')
    instructions_tr = models.TextField(blank=True, default='')
    instructions_en = models.TextField(blank=True, default='')
    exercise_type = models.CharField(max_length=20, choices=ExerciseType.choices)
    difficulty = models.CharField(max_length=10, choices=DifficultyLevel.choices, default=DifficultyLevel.EASY)
    estimated_duration_minutes = models.PositiveIntegerField(default=5)
    icon = models.CharField(max_length=50, default='brain')  # Lucide icon name
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    # Game configuration stored as JSON
    config = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['order', 'difficulty']

    def __str__(self):
        return f"{self.name_en} ({self.get_difficulty_display()})"


class ExerciseSession(TimeStampedModel):
    """
    A patient's exercise session with score and performance data.
    """
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='exercise_sessions',
    )
    exercise = models.ForeignKey(
        CognitiveExercise,
        on_delete=models.CASCADE,
        related_name='sessions',
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)

    # Scoring
    score = models.PositiveIntegerField(default=0)
    max_possible_score = models.PositiveIntegerField(default=100)
    accuracy_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # Detailed results stored as JSON
    results_data = models.JSONField(default=dict, blank=True)

    # Feedback
    difficulty_rating = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text='Patient rating: 1=too easy, 2=good, 3=too hard'
    )
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['patient', '-started_at']),
            models.Index(fields=['exercise', 'patient']),
        ]

    def __str__(self):
        return f"{self.patient} - {self.exercise.name_en}: {self.score}"


class DailyAssessment(TimeStampedModel):
    """
    Daily assessment of patient's cognitive and functional status.
    Can be filled by patient or caregiver.
    """
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='daily_assessments',
    )
    assessment_date = models.DateField()
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_assessments',
    )

    # Mood and Mental State (1-5 scale)
    mood_score = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text='1=Very poor, 5=Excellent'
    )
    confusion_level = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text='1=None, 5=Severe'
    )
    agitation_level = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text='1=None, 5=Severe'
    )
    anxiety_level = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text='1=None, 5=Severe'
    )

    # Sleep
    sleep_quality = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text='1=Very poor, 5=Excellent'
    )
    sleep_hours = models.DecimalField(
        max_digits=4, decimal_places=1,
        null=True, blank=True
    )
    night_wandering = models.BooleanField(null=True, blank=True)

    # Daily Activities (ADL - Activities of Daily Living)
    eating_independence = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text='1=Full assistance, 5=Independent'
    )
    dressing_independence = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text='1=Full assistance, 5=Independent'
    )
    hygiene_independence = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text='1=Full assistance, 5=Independent'
    )
    mobility_independence = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text='1=Full assistance, 5=Independent'
    )

    # Communication
    verbal_communication = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text='1=None, 5=Normal'
    )
    recognition_family = models.BooleanField(
        null=True, blank=True,
        help_text='Recognizes family members'
    )

    # Incidents
    fall_occurred = models.BooleanField(default=False)
    wandering_occurred = models.BooleanField(default=False)
    medication_missed = models.BooleanField(default=False)

    # Notes
    notes = models.TextField(blank=True, default='')
    concerns = models.TextField(blank=True, default='')

    class Meta:
        unique_together = ['patient', 'assessment_date']
        ordering = ['-assessment_date']
        indexes = [
            models.Index(fields=['patient', '-assessment_date']),
        ]

    def __str__(self):
        return f"{self.patient} - {self.assessment_date}"


class CaregiverNote(TimeStampedModel):
    """
    Notes from caregivers about the patient's condition.
    """
    class NoteType(models.TextChoices):
        OBSERVATION = 'observation', 'Observation'
        CONCERN = 'concern', 'Concern'
        IMPROVEMENT = 'improvement', 'Improvement'
        INCIDENT = 'incident', 'Incident'
        MEDICATION = 'medication', 'Medication Related'
        BEHAVIOR = 'behavior', 'Behavior Change'
        OTHER = 'other', 'Other'

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='caregiver_notes',
    )
    caregiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='written_notes',
    )
    note_type = models.CharField(max_length=20, choices=NoteType.choices, default=NoteType.OBSERVATION)
    title = models.CharField(max_length=200)
    content = models.TextField()
    severity = models.PositiveSmallIntegerField(
        default=1,
        help_text='1=Low, 2=Medium, 3=High'
    )
    is_flagged_for_doctor = models.BooleanField(default=False)
    doctor_reviewed = models.BooleanField(default=False)
    doctor_reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient', '-created_at']),
            models.Index(fields=['is_flagged_for_doctor', 'doctor_reviewed']),
        ]

    def __str__(self):
        return f"{self.note_type}: {self.title}"


class CognitiveScore(TimeStampedModel):
    """
    Aggregated cognitive scores over time for tracking progression.
    Calculated periodically from exercise sessions.
    """
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cognitive_scores',
    )
    score_date = models.DateField()

    # Domain scores (0-100)
    memory_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    attention_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    language_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    problem_solving_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    orientation_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # Overall score
    overall_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # Exercise engagement
    exercises_completed = models.PositiveIntegerField(default=0)
    total_exercise_minutes = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ['patient', 'score_date']
        ordering = ['-score_date']

    def __str__(self):
        return f"{self.patient} - {self.score_date}: {self.overall_score}"


class CognitiveScreening(TimeStampedModel):
    """
    Custom cognitive screening assessment - original questions without copyright issues.
    Evaluates: orientation, memory, attention, language, and executive function.
    Total score: 0-100 (percentage based).
    """
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cognitive_screenings',
    )
    assessment_date = models.DateField()
    administered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='administered_screenings',
    )

    # Scores by domain (0-100 each)
    orientation_score = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text='Time and place awareness'
    )
    memory_score = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text='Short-term and recall memory'
    )
    attention_score = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text='Focus and concentration'
    )
    language_score = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text='Naming and comprehension'
    )
    executive_score = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text='Planning and problem solving'
    )

    # Overall calculated score
    total_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Detailed responses stored as JSON
    responses = models.JSONField(default=dict, blank=True)

    # Metadata
    duration_minutes = models.PositiveSmallIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-assessment_date']
        indexes = [
            models.Index(fields=['patient', '-assessment_date']),
        ]

    def calculate_total_score(self):
        """Calculate weighted average of domain scores."""
        scores = [
            self.orientation_score,
            self.memory_score,
            self.attention_score,
            self.language_score,
            self.executive_score,
        ]
        valid_scores = [s for s in scores if s is not None]
        if valid_scores:
            return sum(valid_scores) / len(valid_scores)
        return 0

    def save(self, *args, **kwargs):
        self.total_score = self.calculate_total_score()
        super().save(*args, **kwargs)

    def get_interpretation(self):
        """Return interpretation of the screening score."""
        score = float(self.total_score)
        if score >= 80:
            return 'normal', 'Normal bilişsel fonksiyon'
        elif score >= 60:
            return 'mild', 'Hafif bilişsel zorluk'
        elif score >= 40:
            return 'moderate', 'Orta düzey bilişsel zorluk'
        else:
            return 'severe', 'Ciddi bilişsel zorluk'

    def get_domain_scores(self):
        """Return formatted domain scores."""
        return {
            'orientation': {
                'score': float(self.orientation_score) if self.orientation_score else 0,
                'max': 100,
                'label': 'Yönelim',
            },
            'memory': {
                'score': float(self.memory_score) if self.memory_score else 0,
                'max': 100,
                'label': 'Bellek',
            },
            'attention': {
                'score': float(self.attention_score) if self.attention_score else 0,
                'max': 100,
                'label': 'Dikkat',
            },
            'language': {
                'score': float(self.language_score) if self.language_score else 0,
                'max': 100,
                'label': 'Dil',
            },
            'executive': {
                'score': float(self.executive_score) if self.executive_score else 0,
                'max': 100,
                'label': 'Yürütücü İşlevler',
            },
        }

    def __str__(self):
        return f"{self.patient} - Tarama {self.assessment_date}: {self.total_score}%"
