from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, PatientProfile, DoctorProfile


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == CustomUser.Role.PATIENT:
            PatientProfile.objects.create(user=instance)
        elif instance.role == CustomUser.Role.DOCTOR:
            DoctorProfile.objects.create(user=instance)
