"""
Unit tests for notifications models.
"""

import pytest
from datetime import time
from django.utils import timezone
from apps.notifications.models import Notification, NotificationPreference


@pytest.mark.django_db
class TestNotification:
    """Tests for Notification model."""

    def test_create_notification(self, patient_user):
        """Test creating a notification."""
        notification = Notification.objects.create(
            recipient=patient_user,
            notification_type='reminder',
            title_tr='Ilac Hatirlatmasi',
            title_en='Medication Reminder',
            message_tr='Ilacini alma vakti geldi',
            message_en='Time to take your medication',
        )
        assert notification.recipient == patient_user
        assert notification.notification_type == 'reminder'
        assert notification.is_read is False

    def test_notification_str(self, patient_user):
        """Test notification string representation."""
        notification = Notification.objects.create(
            recipient=patient_user,
            notification_type='info',
            title_tr='Bilgi',
            title_en='Information',
        )
        assert str(notification) == 'info: Information'

    def test_notification_types(self, patient_user):
        """Test all notification type choices."""
        types = ['reminder', 'alert', 'info', 'system']
        for ntype in types:
            notification = Notification.objects.create(
                recipient=patient_user,
                notification_type=ntype,
                title_tr=f'Test {ntype}',
                title_en=f'Test {ntype}',
            )
            assert notification.notification_type == ntype

    def test_mark_as_read(self, patient_user):
        """Test marking notification as read."""
        notification = Notification.objects.create(
            recipient=patient_user,
            notification_type='info',
            title_tr='Test',
            title_en='Test',
        )
        assert notification.is_read is False

        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()

        notification.refresh_from_db()
        assert notification.is_read is True
        assert notification.read_at is not None

    def test_notification_with_action_url(self, patient_user):
        """Test notification with action URL."""
        notification = Notification.objects.create(
            recipient=patient_user,
            notification_type='alert',
            title_tr='Yeni Mesaj',
            title_en='New Message',
            action_url='/messages/123',
        )
        assert notification.action_url == '/messages/123'

    def test_notification_with_metadata(self, patient_user):
        """Test notification with metadata."""
        notification = Notification.objects.create(
            recipient=patient_user,
            notification_type='system',
            title_tr='Sistem',
            title_en='System',
            metadata={'priority': 'high', 'source': 'scheduler'},
        )
        assert notification.metadata['priority'] == 'high'
        assert notification.metadata['source'] == 'scheduler'

    def test_notifications_ordering(self, patient_user):
        """Test notifications are ordered by created_at descending."""
        n1 = Notification.objects.create(
            recipient=patient_user,
            notification_type='info',
            title_tr='First',
            title_en='First',
        )
        n2 = Notification.objects.create(
            recipient=patient_user,
            notification_type='info',
            title_tr='Second',
            title_en='Second',
        )
        notifications = list(Notification.objects.filter(recipient=patient_user))
        assert notifications[0] == n2
        assert notifications[1] == n1

    def test_unread_notifications_filter(self, patient_user):
        """Test filtering unread notifications."""
        Notification.objects.create(
            recipient=patient_user,
            notification_type='info',
            title_tr='Unread',
            title_en='Unread',
            is_read=False,
        )
        Notification.objects.create(
            recipient=patient_user,
            notification_type='info',
            title_tr='Read',
            title_en='Read',
            is_read=True,
        )
        unread = Notification.objects.filter(recipient=patient_user, is_read=False)
        assert unread.count() == 1


@pytest.mark.django_db
class TestNotificationPreference:
    """Tests for NotificationPreference model."""

    def test_create_preference(self, patient_user):
        """Test creating notification preference."""
        pref = NotificationPreference.objects.create(
            user=patient_user,
            email_reminders=True,
            push_reminders=True,
            email_education=True,
            email_product_updates=False,
        )
        assert pref.user == patient_user
        assert pref.email_reminders is True
        assert pref.email_product_updates is False

    def test_preference_str(self, patient_user):
        """Test preference string representation."""
        pref = NotificationPreference.objects.create(user=patient_user)
        assert str(pref) == f"Preferences for {patient_user}"

    def test_default_preferences(self, patient_user):
        """Test default preference values."""
        pref = NotificationPreference.objects.create(user=patient_user)
        assert pref.email_reminders is True
        assert pref.push_reminders is True
        assert pref.email_education is True
        assert pref.email_product_updates is False
        assert pref.quiet_hours_start is None
        assert pref.quiet_hours_end is None

    def test_quiet_hours(self, patient_user):
        """Test setting quiet hours."""
        pref = NotificationPreference.objects.create(
            user=patient_user,
            quiet_hours_start=time(22, 0),
            quiet_hours_end=time(8, 0),
        )
        assert pref.quiet_hours_start == time(22, 0)
        assert pref.quiet_hours_end == time(8, 0)

    def test_one_preference_per_user(self, patient_user):
        """Test only one preference record per user."""
        NotificationPreference.objects.create(user=patient_user)
        with pytest.raises(Exception):
            NotificationPreference.objects.create(user=patient_user)

    def test_disable_all_notifications(self, patient_user):
        """Test disabling all notification types."""
        pref = NotificationPreference.objects.create(
            user=patient_user,
            email_reminders=False,
            push_reminders=False,
            email_education=False,
            email_product_updates=False,
        )
        assert pref.email_reminders is False
        assert pref.push_reminders is False
        assert pref.email_education is False
        assert pref.email_product_updates is False
