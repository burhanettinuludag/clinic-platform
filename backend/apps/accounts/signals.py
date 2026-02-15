import logging

from django.db.models.signals import post_save
from django.contrib.auth.signals import user_login_failed
from django.dispatch import receiver
from .models import CustomUser, PatientProfile, DoctorProfile

security_logger = logging.getLogger('security')


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == CustomUser.Role.PATIENT:
            PatientProfile.objects.create(user=instance)
        elif instance.role == CustomUser.Role.DOCTOR:
            DoctorProfile.objects.create(user=instance)


@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', 'unknown'))
    if ',' in ip:
        ip = ip.split(',')[0].strip()
    email = credentials.get('email', credentials.get('username', 'unknown'))
    security_logger.warning(
        f"Failed login attempt: email={email} ip={ip}"
    )
