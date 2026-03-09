from rest_framework import serializers
from .models import ChatSession, ChatMessage, Conversation, DirectMessage


# ─── AI Chat Serializers ───

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'role', 'content', 'sources', 'confidence',
            'tokens_used', 'llm_provider', 'duration_ms', 'created_at',
        ]
        read_only_fields = fields


class ChatSessionSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatSession
        fields = [
            'id', 'module', 'title', 'message_count',
            'is_active', 'created_at', 'last_message',
        ]
        read_only_fields = ['id', 'title', 'message_count', 'is_active', 'created_at']

    def get_last_message(self, obj):
        msg = obj.messages.order_by('-created_at').first()
        if msg:
            return {
                'role': msg.role,
                'content': msg.content[:100],
                'created_at': msg.created_at.isoformat(),
            }
        return None


class ChatSessionDetailSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatSession
        fields = [
            'id', 'module', 'title', 'message_count',
            'is_active', 'created_at', 'messages',
        ]
        read_only_fields = fields


class AskQuestionSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=2000, min_length=3)


# ─── Doctor Messaging Serializers ───

class DirectMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    sender_role = serializers.CharField(source='sender.role', read_only=True)

    class Meta:
        model = DirectMessage
        fields = [
            'id', 'sender', 'sender_name', 'sender_role',
            'content', 'is_read', 'read_at', 'created_at',
        ]
        read_only_fields = fields

    def get_sender_name(self, obj):
        return obj.sender.get_full_name()


class ConversationListSerializer(serializers.ModelSerializer):
    doctor_name = serializers.SerializerMethodField()
    doctor_specialty = serializers.SerializerMethodField()
    patient_name = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'id', 'patient', 'doctor', 'doctor_name', 'doctor_specialty',
            'patient_name', 'subject', 'status', 'last_message_at',
            'patient_unread_count', 'doctor_unread_count',
            'created_at', 'last_message',
        ]
        read_only_fields = fields

    def get_doctor_name(self, obj):
        return f"Dr. {obj.doctor.get_full_name()}"

    def get_doctor_specialty(self, obj):
        try:
            return obj.doctor.doctor_profile.specialty
        except Exception:
            return ''

    def get_patient_name(self, obj):
        return obj.patient.get_full_name()

    def get_last_message(self, obj):
        msg = obj.messages.order_by('-created_at').first()
        if msg:
            return {
                'sender_name': msg.sender.get_full_name(),
                'content': msg.content[:100],
                'created_at': msg.created_at.isoformat(),
            }
        return None


class ConversationDetailSerializer(serializers.ModelSerializer):
    doctor_name = serializers.SerializerMethodField()
    doctor_specialty = serializers.SerializerMethodField()
    patient_name = serializers.SerializerMethodField()
    messages = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'id', 'patient', 'doctor', 'doctor_name', 'doctor_specialty',
            'patient_name', 'subject', 'status', 'last_message_at',
            'patient_unread_count', 'doctor_unread_count',
            'created_at', 'messages',
        ]
        read_only_fields = fields

    def get_doctor_name(self, obj):
        return f"Dr. {obj.doctor.get_full_name()}"

    def get_doctor_specialty(self, obj):
        try:
            return obj.doctor.doctor_profile.specialty
        except Exception:
            return ''

    def get_patient_name(self, obj):
        return obj.patient.get_full_name()

    def get_messages(self, obj):
        msgs = obj.messages.select_related('sender').order_by('created_at')[:100]
        return DirectMessageSerializer(msgs, many=True).data


class SendMessageSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=5000, min_length=1)


class StartConversationSerializer(serializers.Serializer):
    doctor_id = serializers.UUIDField()
    subject = serializers.CharField(max_length=300, required=False, default='')
    initial_message = serializers.CharField(max_length=5000, min_length=1)


class DoctorListForChatSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    full_name = serializers.CharField()
    specialty = serializers.CharField()
    bio = serializers.CharField()
    headline = serializers.CharField()
    institution = serializers.CharField()
    city = serializers.CharField()
    is_accepting_patients = serializers.BooleanField()
    profile_photo = serializers.ImageField()
    is_verified = serializers.BooleanField()
