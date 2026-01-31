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
