from django.contrib import admin
from .models import ChatSession, ChatMessage, Conversation, DirectMessage


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('patient', 'module', 'title', 'message_count', 'is_active', 'created_at')
    list_filter = ('module', 'is_active')
    search_fields = ('patient__first_name', 'patient__last_name', 'title')
    raw_id_fields = ('patient',)


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'role', 'content_short', 'confidence', 'tokens_used', 'created_at')
    list_filter = ('role', 'confidence')
    raw_id_fields = ('session',)

    def content_short(self, obj):
        return obj.content[:80] + '...' if len(obj.content) > 80 else obj.content
    content_short.short_description = 'Content'


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'subject', 'status', 'last_message_at', 'patient_unread_count', 'doctor_unread_count')
    list_filter = ('status',)
    search_fields = ('patient__first_name', 'patient__last_name', 'doctor__first_name', 'doctor__last_name', 'subject')
    raw_id_fields = ('patient', 'doctor')


@admin.register(DirectMessage)
class DirectMessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'sender', 'content_short', 'is_read', 'created_at')
    list_filter = ('is_read',)
    raw_id_fields = ('conversation', 'sender')

    def content_short(self, obj):
        return obj.content[:80] + '...' if len(obj.content) > 80 else obj.content
    content_short.short_description = 'Content'
