from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedModel


class Notification(TimeStampedModel):
    class NotificationType(models.TextChoices):
        REMINDER = 'reminder', 'Reminder'
        ALERT = 'alert', 'Alert'
        INFO = 'info', 'Information'
        SYSTEM = 'system', 'System'

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    notification_type = models.CharField(max_length=20, choices=NotificationType.choices)
    title_tr = models.CharField(max_length=300)
    title_en = models.CharField(max_length=300)
    message_tr = models.TextField(blank=True, default='')
    message_en = models.TextField(blank=True, default='')
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    action_url = models.CharField(max_length=500, blank=True, default='')
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read', '-created_at']),
        ]

    def __str__(self):
        return f"{self.notification_type}: {self.title_en}"


class NotificationPreference(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences',
    )
    email_reminders = models.BooleanField(default=True)
    push_reminders = models.BooleanField(default=True)
    email_education = models.BooleanField(default=True)
    email_product_updates = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"Preferences for {self.user}"
