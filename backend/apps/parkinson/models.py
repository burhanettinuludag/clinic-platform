from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.common.models import TimeStampedModel


# ============================================================
# TETİKLEYİCİLER
# ============================================================

class ParkinsonTrigger(TimeStampedModel):
    """Parkinson semptomlarını tetikleyebilecek faktörler."""

    class TriggerCategory(models.TextChoices):
        MEDICATION = 'medication', 'Medication Related'
        STRESS = 'stress', 'Stress / Emotional'
        PHYSICAL = 'physical', 'Physical'
        ENVIRONMENTAL = 'environmental', 'Environmental'
        DIETARY = 'dietary', 'Dietary'
        SLEEP = 'sleep', 'Sleep Related'
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
        related_name='custom_parkinson_triggers',
    )

    class Meta:
        ordering = ['category', 'name_en']

    def __str__(self):
        return self.name_en


# ============================================================
# SEMPTOM GÜNLÜKLERİ
# ============================================================

class ParkinsonSymptomEntry(TimeStampedModel):
    """Günlük Parkinson semptom kaydı."""

    class MotorState(models.TextChoices):
        ON = 'on', 'ON (İlaç etkili)'
        OFF = 'off', 'OFF (İlaç etkisiz)'
        DYSKINESIA = 'dyskinesia', 'Diskinezi'
        WEARING_OFF = 'wearing_off', 'İlaç etkisi azalıyor'

    class AffectedSide(models.TextChoices):
        LEFT = 'left', 'Left'
        RIGHT = 'right', 'Right'
        BILATERAL = 'bilateral', 'Bilateral'

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='parkinson_symptoms',
    )
    recorded_at = models.DateTimeField()
    motor_state = models.CharField(
        max_length=15,
        choices=MotorState.choices,
        blank=True,
        default='',
    )
    affected_side = models.CharField(
        max_length=15,
        choices=AffectedSide.choices,
        blank=True,
        default='',
    )

    # Motor semptomlar (0-4 şiddet: 0=yok, 1=hafif, 2=orta, 3=şiddetli, 4=çok şiddetli)
    tremor_severity = models.PositiveSmallIntegerField(
        default=0,
        validators=[MaxValueValidator(4)],
        help_text='Tremor şiddeti 0-4',
    )
    rigidity_severity = models.PositiveSmallIntegerField(
        default=0,
        validators=[MaxValueValidator(4)],
        help_text='Rijidite şiddeti 0-4',
    )
    bradykinesia_severity = models.PositiveSmallIntegerField(
        default=0,
        validators=[MaxValueValidator(4)],
        help_text='Bradikinezi şiddeti 0-4',
    )
    postural_instability = models.PositiveSmallIntegerField(
        default=0,
        validators=[MaxValueValidator(4)],
        help_text='Postüral instabilite 0-4',
    )
    gait_difficulty = models.PositiveSmallIntegerField(
        default=0,
        validators=[MaxValueValidator(4)],
        help_text='Yürüme güçlüğü 0-4',
    )

    # Non-motor semptomlar
    has_freezing = models.BooleanField(default=False, help_text='Donma (freezing) atağı')
    has_balance_problem = models.BooleanField(default=False, help_text='Denge sorunu')
    has_speech_difficulty = models.BooleanField(default=False, help_text='Konuşma güçlüğü')
    has_swallowing_difficulty = models.BooleanField(default=False, help_text='Yutma güçlüğü')
    has_sleep_disturbance = models.BooleanField(default=False, help_text='Uyku bozukluğu')
    has_constipation = models.BooleanField(default=False, help_text='Kabızlık')
    has_mood_change = models.BooleanField(default=False, help_text='Duygu durum değişikliği')
    has_cognitive_issue = models.BooleanField(default=False, help_text='Bilişsel sorun')
    has_pain = models.BooleanField(default=False, help_text='Ağrı')
    has_fatigue = models.BooleanField(default=False, help_text='Yorgunluk')

    # Genel durum
    overall_severity = models.PositiveSmallIntegerField(
        default=0,
        validators=[MaxValueValidator(10)],
        help_text='Genel semptom şiddeti 0-10',
    )
    on_time_hours = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True,
        help_text='Gün içinde ON süre (saat)',
    )
    off_time_hours = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True,
        help_text='Gün içinde OFF süre (saat)',
    )

    triggers_identified = models.ManyToManyField(
        ParkinsonTrigger, blank=True, related_name='symptom_entries',
    )
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['patient', '-recorded_at']),
        ]
        verbose_name_plural = 'Parkinson symptom entries'

    def __str__(self):
        return f"Parkinson symptoms {self.recorded_at.date()} - Severity: {self.overall_severity}"


# ============================================================
# İLAÇ YÖNETİMİ (Parkinson'a özel)
# ============================================================

class ParkinsonMedication(TimeStampedModel):
    """Parkinson ilaçları ve LED (Levodopa Eşdeğer Doz) bilgisi."""

    class DrugClass(models.TextChoices):
        LEVODOPA = 'levodopa', 'Levodopa / Karbidopa'
        DOPAMINE_AGONIST = 'dopamine_agonist', 'Dopamin Agonisti'
        MAO_B_INHIBITOR = 'mao_b_inhibitor', 'MAO-B İnhibitörü'
        COMT_INHIBITOR = 'comt_inhibitor', 'COMT İnhibitörü'
        AMANTADINE = 'amantadine', 'Amantadin'
        ANTICHOLINERGIC = 'anticholinergic', 'Antikolinerjik'
        OTHER = 'other', 'Diğer'

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='parkinson_medications',
    )
    name = models.CharField(max_length=200, help_text='İlaç adı (ör. Madopar 250mg)')
    generic_name = models.CharField(max_length=200, blank=True, default='', help_text='Etken madde')
    drug_class = models.CharField(max_length=20, choices=DrugClass.choices)
    dosage_mg = models.DecimalField(
        max_digits=7, decimal_places=2,
        help_text='Doz (mg)',
    )
    frequency_per_day = models.PositiveSmallIntegerField(
        default=1,
        help_text='Günde kaç kez',
    )
    led_conversion_factor = models.DecimalField(
        max_digits=5, decimal_places=2, default=1.0,
        help_text='LED dönüşüm faktörü (ör. Levodopa=1.0, Pramipexole=100)',
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-is_active', 'drug_class', 'name']
        indexes = [
            models.Index(fields=['patient', '-is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.dosage_mg}mg x{self.frequency_per_day})"

    @property
    def daily_led(self):
        """Günlük Levodopa Eşdeğer Dozu hesapla."""
        return float(self.dosage_mg) * self.frequency_per_day * float(self.led_conversion_factor)


class ParkinsonMedicationSchedule(TimeStampedModel):
    """İlaç alım saatleri (hatırlatıcı için)."""

    medication = models.ForeignKey(
        ParkinsonMedication,
        on_delete=models.CASCADE,
        related_name='schedules',
    )
    time_of_day = models.TimeField(help_text='Alım saati')
    label = models.CharField(
        max_length=50, blank=True, default='',
        help_text='Etiket (ör. Sabah, Öğle, Akşam)',
    )
    is_enabled = models.BooleanField(default=True)

    class Meta:
        ordering = ['time_of_day']

    def __str__(self):
        return f"{self.medication.name} - {self.time_of_day}"


class ParkinsonMedicationLog(TimeStampedModel):
    """İlaç alım kaydı (alındı mı, motor durum)."""

    medication = models.ForeignKey(
        ParkinsonMedication,
        on_delete=models.CASCADE,
        related_name='logs',
    )
    schedule = models.ForeignKey(
        ParkinsonMedicationSchedule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs',
    )
    scheduled_time = models.DateTimeField(help_text='Planlanan alım zamanı')
    taken_at = models.DateTimeField(null=True, blank=True, help_text='Gerçek alım zamanı')
    was_taken = models.BooleanField(default=False)
    motor_state_before = models.CharField(
        max_length=15,
        choices=ParkinsonSymptomEntry.MotorState.choices,
        blank=True,
        default='',
    )
    motor_state_after = models.CharField(
        max_length=15,
        choices=ParkinsonSymptomEntry.MotorState.choices,
        blank=True,
        default='',
    )
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-scheduled_time']
        indexes = [
            models.Index(fields=['medication', '-scheduled_time']),
        ]

    def __str__(self):
        status = 'Alındı' if self.was_taken else 'Alınmadı'
        return f"{self.medication.name} - {self.scheduled_time.date()} - {status}"


# ============================================================
# KLİNİK DEĞERLENDİRMELER
# ============================================================

class HoehnYahrAssessment(TimeStampedModel):
    """Hoehn & Yahr Evreleme Ölçeği (telif-free)."""

    class Stage(models.TextChoices):
        STAGE_0 = '0', 'Evre 0 - Hastalık belirtisi yok'
        STAGE_1 = '1', 'Evre 1 - Tek taraflı tutulum'
        STAGE_1_5 = '1.5', 'Evre 1.5 - Tek taraflı + aksiyel tutulum'
        STAGE_2 = '2', 'Evre 2 - İki taraflı, denge sorunu yok'
        STAGE_2_5 = '2.5', 'Evre 2.5 - Hafif iki taraflı, çekme testinde düzelme'
        STAGE_3 = '3', 'Evre 3 - İki taraflı, hafif-orta; postüral instabilite'
        STAGE_4 = '4', 'Evre 4 - Ciddi engel, yardımsız yürüyebilir'
        STAGE_5 = '5', 'Evre 5 - Tekerlekli sandalye/yatağa bağımlı'

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='hoehn_yahr_assessments',
    )
    assessed_at = models.DateTimeField()
    stage = models.CharField(max_length=5, choices=Stage.choices)
    assessed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hoehn_yahr_conducted',
    )
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-assessed_at']
        indexes = [
            models.Index(fields=['patient', '-assessed_at']),
        ]

    def __str__(self):
        return f"H&Y Stage {self.stage} - {self.assessed_at.date()}"


class SchwabEnglandAssessment(TimeStampedModel):
    """Schwab & England Günlük Yaşam Aktiviteleri Ölçeği (telif-free)."""

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='schwab_england_assessments',
    )
    assessed_at = models.DateTimeField()
    score = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(100)],
        help_text='Skor 0-100 (10 ar artışlarla; 100=tam bağımsız, 0=yatalak)',
    )
    assessed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='schwab_england_conducted',
    )
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-assessed_at']
        indexes = [
            models.Index(fields=['patient', '-assessed_at']),
        ]

    def __str__(self):
        return f"S&E {self.score}% - {self.assessed_at.date()}"


class NMSQuestAssessment(TimeStampedModel):
    """NMSQuest - Non-Motor Semptomlar Tarama Anketi (30 soru, evet/hayır)."""

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='nmsquest_assessments',
    )
    assessed_at = models.DateTimeField()

    # 30 evet/hayır sorusu (domain grupları)
    # Gastrointestinal
    q1_drooling = models.BooleanField(default=False, help_text='Ağızdan salya akması')
    q2_dysphagia = models.BooleanField(default=False, help_text='Yutma güçlüğü')
    q3_constipation = models.BooleanField(default=False, help_text='Kabızlık')
    # Üriner
    q4_urinary_urgency = models.BooleanField(default=False, help_text='İdrar sıkışması')
    q5_nocturia = models.BooleanField(default=False, help_text='Gece idrara çıkma')
    # Otonom
    q6_dizziness = models.BooleanField(default=False, help_text='Baş dönmesi (ortostatik)')
    q7_sweating = models.BooleanField(default=False, help_text='Aşırı terleme')
    q8_sexual_dysfunction = models.BooleanField(default=False, help_text='Cinsel işlev bozukluğu')
    # Uyku
    q9_insomnia = models.BooleanField(default=False, help_text='Uykuya dalamama')
    q10_daytime_sleepiness = models.BooleanField(default=False, help_text='Gündüz aşırı uyuklama')
    q11_rbd = models.BooleanField(default=False, help_text='REM uyku davranış bozukluğu')
    q12_restless_legs = models.BooleanField(default=False, help_text='Huzursuz bacak')
    # Duygu durum
    q13_depression = models.BooleanField(default=False, help_text='Depresif ruh hali')
    q14_anxiety = models.BooleanField(default=False, help_text='Anksiyete/endişe')
    q15_apathy = models.BooleanField(default=False, help_text='İlgisizlik/apati')
    # Bilişsel
    q16_attention_difficulty = models.BooleanField(default=False, help_text='Dikkat güçlüğü')
    q17_memory_problem = models.BooleanField(default=False, help_text='Bellek sorunu')
    q18_hallucination = models.BooleanField(default=False, help_text='Halüsinasyon')
    # Ağrı / Duyusal
    q19_pain = models.BooleanField(default=False, help_text='Ağrı')
    q20_numbness = models.BooleanField(default=False, help_text='Uyuşma/karıncalanma')
    q21_taste_smell = models.BooleanField(default=False, help_text='Tat/koku değişikliği')
    # Diğer
    q22_weight_change = models.BooleanField(default=False, help_text='Kilo değişikliği')
    q23_fatigue = models.BooleanField(default=False, help_text='Yorgunluk')
    q24_double_vision = models.BooleanField(default=False, help_text='Çift görme')
    q25_speech = models.BooleanField(default=False, help_text='Konuşma değişikliği')
    q26_falling = models.BooleanField(default=False, help_text='Düşme')
    q27_freezing = models.BooleanField(default=False, help_text='Donma')
    q28_leg_swelling = models.BooleanField(default=False, help_text='Bacak şişmesi')
    q29_excessive_saliva = models.BooleanField(default=False, help_text='Aşırı tükürük')
    q30_unexplained_fever = models.BooleanField(default=False, help_text='Açıklanamayan ateş')

    total_score = models.PositiveSmallIntegerField(
        default=0,
        help_text='Toplam skor (0-30)',
    )
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-assessed_at']
        indexes = [
            models.Index(fields=['patient', '-assessed_at']),
        ]

    def __str__(self):
        return f"NMSQuest {self.total_score}/30 - {self.assessed_at.date()}"

    def calculate_total(self):
        """Evet yanıtlarını say."""
        total = 0
        for i in range(1, 31):
            field_name = [f for f in dir(self) if f.startswith(f'q{i}_')]
            if field_name and getattr(self, field_name[0], False):
                total += 1
        self.total_score = total
        return total


class NoseraMotorAssessment(TimeStampedModel):
    """Norosera Motor Değerlendirme Formu (telif-free, 10 madde, 0-40)."""

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='nosera_motor_assessments',
    )
    assessed_at = models.DateTimeField()

    # 10 madde, her biri 0-4 (0=normal, 1=hafif, 2=orta, 3=şiddetli, 4=çok şiddetli)
    tremor_rest = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(4)])
    tremor_action = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(4)])
    rigidity = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(4)])
    finger_tapping = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(4)])
    hand_movements = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(4)])
    leg_agility = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(4)])
    arising_from_chair = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(4)])
    gait = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(4)])
    postural_stability = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(4)])
    body_bradykinesia = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(4)])

    total_score = models.PositiveSmallIntegerField(default=0, help_text='0-40')
    assessed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='nosera_motor_conducted',
    )
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-assessed_at']
        indexes = [
            models.Index(fields=['patient', '-assessed_at']),
        ]

    def __str__(self):
        return f"Norosera Motor {self.total_score}/40 - {self.assessed_at.date()}"

    def calculate_total(self):
        self.total_score = (
            self.tremor_rest + self.tremor_action + self.rigidity
            + self.finger_tapping + self.hand_movements + self.leg_agility
            + self.arising_from_chair + self.gait + self.postural_stability
            + self.body_bradykinesia
        )
        return self.total_score


class NoseraDailyLivingAssessment(TimeStampedModel):
    """Norosera Günlük Yaşam Aktiviteleri Formu (12 madde, 0-48)."""

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='nosera_daily_assessments',
    )
    assessed_at = models.DateTimeField()

    # 12 madde, her biri 0-4
    speech = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(4)])
    salivation = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(4)])
    swallowing = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(4)])
    handwriting = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(4)])
    cutting_food = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(4)])
    dressing = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(4)])
    hygiene = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(4)])
    turning_in_bed = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(4)])
    falling = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(4)])
    freezing = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(4)])
    walking = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(4)])
    tremor_impact = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(4)])

    total_score = models.PositiveSmallIntegerField(default=0, help_text='0-48')
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-assessed_at']
        indexes = [
            models.Index(fields=['patient', '-assessed_at']),
        ]

    def __str__(self):
        return f"Norosera Daily Living {self.total_score}/48 - {self.assessed_at.date()}"

    def calculate_total(self):
        self.total_score = (
            self.speech + self.salivation + self.swallowing + self.handwriting
            + self.cutting_food + self.dressing + self.hygiene + self.turning_in_bed
            + self.falling + self.freezing + self.walking + self.tremor_impact
        )
        return self.total_score


# ============================================================
# VİZİT KAYDI
# ============================================================

class ParkinsonVisit(TimeStampedModel):
    """Doktor ziyaret kaydı."""

    class VisitType(models.TextChoices):
        ROUTINE = 'routine', 'Rutin Kontrol'
        EMERGENCY = 'emergency', 'Acil'
        MEDICATION_ADJUSTMENT = 'medication_adjustment', 'İlaç Ayarlaması'
        INITIAL = 'initial', 'İlk Muayene'
        FOLLOW_UP = 'follow_up', 'Takip'

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='parkinson_visits',
    )
    visit_date = models.DateTimeField()
    visit_type = models.CharField(max_length=25, choices=VisitType.choices, default=VisitType.ROUTINE)
    doctor_name = models.CharField(max_length=200, blank=True, default='')
    hospital_name = models.CharField(max_length=300, blank=True, default='')

    # Değerlendirme linkleri
    hoehn_yahr = models.ForeignKey(
        HoehnYahrAssessment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='visits',
    )
    schwab_england = models.ForeignKey(
        SchwabEnglandAssessment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='visits',
    )

    # LED özet
    total_daily_led = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        help_text='Toplam günlük LED (mg)',
    )
    medication_changes = models.TextField(blank=True, default='', help_text='İlaç değişiklikleri özeti')
    findings = models.TextField(blank=True, default='', help_text='Muayene bulguları')
    plan = models.TextField(blank=True, default='', help_text='Tedavi planı')
    next_visit_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-visit_date']
        indexes = [
            models.Index(fields=['patient', '-visit_date']),
        ]

    def __str__(self):
        return f"Visit {self.visit_date.date()} - {self.get_visit_type_display()}"
