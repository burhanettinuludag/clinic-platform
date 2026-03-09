from django.conf import settings
from django.db import models
from apps.common.models import TimeStampedModel


class ChatSession(TimeStampedModel):
    """Hasta - AI sohbet oturumu. Her modul icin ayri oturum."""

    class Module(models.TextChoices):
        GENERAL = 'general', 'Genel'
        MIGRAINE = 'migraine', 'Migren'
        EPILEPSY = 'epilepsy', 'Epilepsi'
        DEMENTIA = 'dementia', 'Demans'

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_sessions',
    )
    module = models.CharField(
        max_length=20,
        choices=Module.choices,
        default=Module.GENERAL,
    )
    title = models.CharField(max_length=200, blank=True, default='')
    is_active = models.BooleanField(default=True)
    message_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient', 'module', '-created_at']),
        ]

    def __str__(self):
        return f"Chat: {self.patient.get_full_name()} - {self.get_module_display()} ({self.title or 'Yeni'})"


class ChatMessage(TimeStampedModel):
    """AI sohbet mesaji (user veya assistant)."""

    class Role(models.TextChoices):
        USER = 'user', 'User'
        ASSISTANT = 'assistant', 'Assistant'

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    role = models.CharField(max_length=10, choices=Role.choices)
    content = models.TextField()
    sources = models.JSONField(default=list, blank=True)
    confidence = models.CharField(max_length=10, blank=True, default='')
    tokens_used = models.PositiveIntegerField(default=0)
    llm_provider = models.CharField(max_length=20, blank=True, default='')
    duration_ms = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"[{self.role}] {self.content[:50]}..."


class Conversation(TimeStampedModel):
    """Hasta - Doktor mesajlasma konusmasi."""

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Aktif'
        CLOSED = 'closed', 'Kapali'
        ARCHIVED = 'archived', 'Arsivlenmis'

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient_conversations',
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_conversations',
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    subject = models.CharField(max_length=300, blank=True, default='')
    last_message_at = models.DateTimeField(null=True, blank=True)
    patient_unread_count = models.PositiveIntegerField(default=0)
    doctor_unread_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-last_message_at']
        indexes = [
            models.Index(fields=['patient', '-last_message_at']),
            models.Index(fields=['doctor', '-last_message_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Conversation: {self.patient.get_full_name()} <-> Dr. {self.doctor.get_full_name()}"


class DirectMessage(TimeStampedModel):
    """Doktor-hasta arasi mesaj."""

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_direct_messages',
    )
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
        ]

    def __str__(self):
        return f"[{self.sender.get_full_name()}] {self.content[:50]}..."
