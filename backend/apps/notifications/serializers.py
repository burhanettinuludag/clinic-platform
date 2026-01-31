from rest_framework import serializers
from .models import Notification, NotificationPreference


class NotificationSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    message = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'title', 'message',
            'is_read', 'read_at', 'action_url', 'metadata', 'created_at',
        ]

    def _get_lang(self):
        request = self.context.get('request')
        if request and hasattr(request, 'headers'):
            return request.headers.get('Accept-Language', 'tr')[:2]
        return 'tr'

    def get_title(self, obj):
        return getattr(obj, f'title_{self._get_lang()}', obj.title_tr)

    def get_message(self, obj):
        return getattr(obj, f'message_{self._get_lang()}', obj.message_tr)


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = [
            'email_reminders', 'push_reminders', 'email_education',
            'email_product_updates', 'quiet_hours_start', 'quiet_hours_end',
        ]
