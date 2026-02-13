from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from apps.common.models import TimeStampedModel


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', CustomUser.Role.ADMIN)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        PATIENT = 'patient', 'Patient'
        DOCTOR = 'doctor', 'Doctor'
        ADMIN = 'admin', 'Admin'

    username = None
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.PATIENT)
    phone = models.CharField(max_length=20, blank=True, default='')
    preferred_language = models.CharField(
        max_length=5,
        choices=[('tr', 'Turkce'), ('en', 'English')],
        default='tr',
    )
    is_email_verified = models.BooleanField(default=False)
    kvkk_consent_date = models.DateTimeField(null=True, blank=True)
    last_active = models.DateTimeField(null=True, blank=True)

    objects = CustomUserManager()

    class Meta:
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"


class PatientProfile(TimeStampedModel):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='patient_profile',
    )
    assigned_doctor = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_patients',
        limit_choices_to={'role': 'doctor'},
    )
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=10,
        choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        blank=True,
        default='',
    )
    emergency_contact_name = models.CharField(max_length=150, blank=True, default='')
    emergency_contact_phone = models.CharField(max_length=20, blank=True, default='')
    notes = models.TextField(blank=True, default='')

    class Meta:
        indexes = [
            models.Index(fields=['assigned_doctor']),
        ]

    def __str__(self):
        return f"Patient: {self.user.get_full_name()}"


class DoctorProfile(TimeStampedModel):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='doctor_profile',
    )
    specialty = models.CharField(max_length=100, blank=True, default='')
    license_number = models.CharField(max_length=50, blank=True, default='')
    bio = models.TextField(blank=True, default='')
    is_accepting_patients = models.BooleanField(default=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name()}"


class DoctorAuthor(TimeStampedModel):
    """Doktor yazar profili. Platform uzerinde yazi yazan hekimlerin detayli profili."""

    SPECIALTY_CHOICES = [
        ('neurology', 'Noroloji'),
        ('ftr', 'Fiziksel Tip ve Rehabilitasyon'),
        ('neurosurgery', 'Beyin ve Sinir Cerrahisi'),
        ('physiology', 'Fizyoloji'),
        ('geriatrics', 'Geriatri'),
        ('psychiatry', 'Psikiyatri'),
        ('sleep_medicine', 'Uyku Bozukluklari'),
        ('clinical_psychology', 'Klinik Psikoloji'),
        ('social_work', 'Sosyal Hizmet'),
    ]

    AUTHOR_LEVELS = [
        (0, 'Yeni Yazar'),
        (1, 'Onayli Yazar'),
        (2, 'Aktif Yazar'),
        (3, 'Kidemli Yazar'),
        (4, 'Editor'),
    ]

    doctor = models.OneToOneField(DoctorProfile, on_delete=models.CASCADE, related_name='author_profile')
    primary_specialty = models.CharField(max_length=30, choices=SPECIALTY_CHOICES)
    secondary_specialties = models.JSONField(default=list, blank=True)
    sub_specialties = models.JSONField(default=list, blank=True)
    bio_tr = models.TextField(blank=True, default='')
    bio_en = models.TextField(blank=True, default='')
    headline_tr = models.CharField(max_length=200, blank=True, default='')
    headline_en = models.CharField(max_length=200, blank=True, default='')
    education = models.JSONField(default=list, blank=True)
    publications = models.JSONField(default=list, blank=True)
    memberships = models.JSONField(default=list, blank=True)
    orcid_id = models.CharField(max_length=50, blank=True, default='')
    google_scholar_url = models.URLField(blank=True, default='')
    pubmed_author_id = models.CharField(max_length=50, blank=True, default='')
    institution = models.CharField(max_length=200, blank=True, default='')
    department = models.CharField(max_length=200, blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')
    author_level = models.IntegerField(choices=AUTHOR_LEVELS, default=0)
    total_articles = models.PositiveIntegerField(default=0)
    total_views = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_document = models.FileField(upload_to='doctor_verification/', blank=True)
    profile_photo = models.ImageField(upload_to='doctor_photos/', blank=True)
    linkedin_url = models.URLField(blank=True, default='')
    website_url = models.URLField(blank=True, default='')
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Doktor Yazar'
        verbose_name_plural = 'Doktor Yazarlar'
        ordering = ['-author_level', '-total_articles']

    def __str__(self):
        return f"{self.doctor.user.get_full_name()} - {self.get_primary_specialty_display()}"

    def update_level(self):
        if self.total_articles >= 50:
            self.author_level = 4
        elif self.total_articles >= 25:
            self.author_level = 3
        elif self.total_articles >= 10:
            self.author_level = 2
        elif self.total_articles >= 5:
            self.author_level = 1
        else:
            self.author_level = 0
        self.save(update_fields=['author_level'])

    @property
    def can_auto_publish(self):
        return self.author_level >= 2

    @property
    def min_publish_score(self):
        return {0: 999, 1: 80, 2: 70, 3: 60, 4: 0}.get(self.author_level, 999)
