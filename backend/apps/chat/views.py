import logging
import time

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.permissions import IsPatient, IsDoctor
from .models import ChatSession, ChatMessage, Conversation, DirectMessage
from .serializers import (
    ChatSessionSerializer, ChatSessionDetailSerializer, ChatMessageSerializer,
    AskQuestionSerializer, ConversationListSerializer, ConversationDetailSerializer,
    DirectMessageSerializer, SendMessageSerializer, StartConversationSerializer,
    DoctorListForChatSerializer,
)

User = get_user_model()
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# Feature A: AI Chat
# ─────────────────────────────────────────────

class ChatSessionViewSet(viewsets.ModelViewSet):
    """
    AI saglik asistani sohbet oturumlari.
    Hasta modullere gore soru sorabilir, RAG tabanli yanit alir.
    """
    permission_classes = [permissions.IsAuthenticated, IsPatient]
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        qs = ChatSession.objects.filter(patient=self.request.user, is_active=True)
        module = self.request.query_params.get('module')
        if module:
            qs = qs.filter(module=module)
        return qs

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ChatSessionDetailSerializer
        return ChatSessionSerializer

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=['is_active'])

    @action(detail=True, methods=['post'], url_path='ask')
    def ask_question(self, request, pk=None):
        """Soru sor - QA Agent ile RAG tabanli yanit."""
        session = self.get_object()

        serializer = AskQuestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question = serializer.validated_data['question']

        # Rate limit: gunde max 50 soru
        today = timezone.now().date()
        today_count = ChatMessage.objects.filter(
            session__patient=request.user,
            role='user',
            created_at__date=today,
        ).count()
        if today_count >= 50:
            return Response(
                {'error': 'Gunluk soru limitine ulastiniz (50). Yarin tekrar deneyin.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        # Kullanici mesajini kaydet
        user_msg = ChatMessage.objects.create(
            session=session,
            role='user',
            content=question,
        )

        # Ilk mesajsa oturum basligini ayarla
        if not session.title:
            session.title = question[:100]
            session.save(update_fields=['title'])

        # QA Agent ile yanit uret
        try:
            from services.registry import agent_registry

            qa_agent = agent_registry.get('qa_agent')
            if not qa_agent:
                return Response(
                    {'error': 'AI asistan gecici olarak kullanilamiyor.'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )

            start_time = time.time()

            # Onceki mesajlardan context olustur (son 6 mesaj)
            recent_msgs = ChatMessage.objects.filter(
                session=session,
            ).order_by('-created_at')[:6]
            history_context = ''
            if recent_msgs.count() > 1:
                history_parts = []
                for msg in reversed(list(recent_msgs)):
                    if msg.id != user_msg.id:
                        role_label = 'Hasta' if msg.role == 'user' else 'Asistan'
                        history_parts.append(f"{role_label}: {msg.content[:200]}")
                if history_parts:
                    history_context = '\n'.join(history_parts[-4:])

            language = request.user.preferred_language or 'tr'
            input_data = {
                'question': question,
                'language': language,
                'module': session.module if session.module != 'general' else None,
            }

            if history_context:
                input_data['question'] = (
                    f"Onceki konusma:\n{history_context}\n\nYeni soru: {question}"
                )

            result = qa_agent.run(
                input_data=input_data,
                triggered_by=request.user,
            )

            duration_ms = int((time.time() - start_time) * 1000)

            if result.success:
                answer = result.data.get('answer', '')
                sources = result.data.get('sources', [])
                confidence = result.data.get('confidence', 'medium')
                disclaimer = result.data.get('disclaimer', '')

                if disclaimer and disclaimer not in answer:
                    answer = f"{answer}\n\n---\n{disclaimer}"

                assistant_msg = ChatMessage.objects.create(
                    session=session,
                    role='assistant',
                    content=answer,
                    sources=sources,
                    confidence=confidence,
                    tokens_used=result.tokens_used,
                    llm_provider=result.provider,
                    duration_ms=duration_ms,
                )
            else:
                error_answer = (
                    'Yanitiniz olusturulurken bir sorun olustu. Lutfen tekrar deneyin.'
                    if language == 'tr'
                    else 'An error occurred while generating your answer. Please try again.'
                )
                assistant_msg = ChatMessage.objects.create(
                    session=session,
                    role='assistant',
                    content=error_answer,
                    confidence='low',
                    duration_ms=duration_ms,
                )

        except Exception as e:
            logger.error(f"AI Chat error: {e}")
            assistant_msg = ChatMessage.objects.create(
                session=session,
                role='assistant',
                content='Teknik bir sorun olustu. Lutfen daha sonra tekrar deneyin.',
                confidence='low',
            )

        # Mesaj sayisini guncelle
        session.message_count = session.messages.count()
        session.save(update_fields=['message_count'])

        return Response({
            'user_message': ChatMessageSerializer(user_msg).data,
            'assistant_message': ChatMessageSerializer(assistant_msg).data,
        })


# ─────────────────────────────────────────────
# Feature B: Doctor-Patient Messaging (Hasta)
# ─────────────────────────────────────────────

class DoctorListView(generics.ListAPIView):
    """Mesajlasma icin uygun doktor listesi."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DoctorListForChatSerializer

    def get_queryset(self):
        return None  # custom list

    def list(self, request, *args, **kwargs):
        from apps.accounts.models import DoctorProfile, DoctorAuthor

        profiles = DoctorProfile.objects.filter(
            is_accepting_patients=True,
        ).select_related('user')

        specialty = request.query_params.get('specialty')
        search = request.query_params.get('search')

        if specialty:
            profiles = profiles.filter(specialty__icontains=specialty)
        if search:
            profiles = profiles.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search)
            )

        language = request.headers.get('Accept-Language', 'tr')[:2]

        doctors = []
        for profile in profiles[:50]:
            # DoctorAuthor bilgilerini al (varsa)
            author_data = {}
            try:
                author = profile.author_profile
                author_data = {
                    'headline': getattr(author, f'headline_{language}', '') or author.headline_tr,
                    'institution': author.institution,
                    'city': author.city,
                    'profile_photo': author.profile_photo.url if author.profile_photo else None,
                    'is_verified': author.is_verified,
                }
            except DoctorAuthor.DoesNotExist:
                author_data = {
                    'headline': '',
                    'institution': '',
                    'city': '',
                    'profile_photo': None,
                    'is_verified': False,
                }

            doctors.append({
                'id': str(profile.user.id),
                'full_name': f"Dr. {profile.user.get_full_name()}",
                'specialty': profile.specialty,
                'bio': profile.bio[:200] if profile.bio else '',
                'is_accepting_patients': profile.is_accepting_patients,
                **author_data,
            })

        return Response(doctors)


class ConversationViewSet(viewsets.ModelViewSet):
    """Hasta tarafli mesajlasma konusmalari."""
    permission_classes = [permissions.IsAuthenticated, IsPatient]
    http_method_names = ['get', 'post']

    def get_queryset(self):
        return Conversation.objects.filter(
            patient=self.request.user,
        ).select_related('doctor').exclude(status='archived')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ConversationDetailSerializer
        return ConversationListSerializer

    def create(self, request, *args, **kwargs):
        """Yeni konusma baslat."""
        serializer = StartConversationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        doctor_id = serializer.validated_data['doctor_id']
        subject = serializer.validated_data.get('subject', '')
        initial_message = serializer.validated_data['initial_message']

        try:
            doctor = User.objects.get(id=doctor_id, role='doctor')
        except User.DoesNotExist:
            return Response(
                {'error': 'Doktor bulunamadi.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Doktor hasta kabul ediyor mu?
        try:
            if not doctor.doctor_profile.is_accepting_patients:
                return Response(
                    {'error': 'Bu doktor su anda yeni hasta kabul etmiyor.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception:
            pass

        conversation = Conversation.objects.create(
            patient=request.user,
            doctor=doctor,
            subject=subject,
            last_message_at=timezone.now(),
            doctor_unread_count=1,
        )

        DirectMessage.objects.create(
            conversation=conversation,
            sender=request.user,
            content=initial_message,
        )

        # Doktora bildirim gonder
        _notify_new_message(doctor, request.user, conversation)

        return Response(
            ConversationDetailSerializer(conversation).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['post'], url_path='send')
    def send_message(self, request, pk=None):
        """Mesaj gonder."""
        conversation = self.get_object()

        if conversation.status != 'active':
            return Response(
                {'error': 'Bu konusma kapatilmis.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        msg = DirectMessage.objects.create(
            conversation=conversation,
            sender=request.user,
            content=serializer.validated_data['content'],
        )

        conversation.last_message_at = timezone.now()
        conversation.doctor_unread_count += 1
        conversation.save(update_fields=['last_message_at', 'doctor_unread_count'])

        _notify_new_message(conversation.doctor, request.user, conversation)

        return Response(DirectMessageSerializer(msg).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='close')
    def close_conversation(self, request, pk=None):
        """Konusmayi kapat."""
        conversation = self.get_object()
        conversation.status = 'closed'
        conversation.save(update_fields=['status'])
        return Response({'status': 'closed'})

    @action(detail=True, methods=['post'], url_path='mark-read')
    def mark_read(self, request, pk=None):
        """Okunmamis mesajlari okundu isaretle."""
        conversation = self.get_object()

        DirectMessage.objects.filter(
            conversation=conversation,
            is_read=False,
        ).exclude(sender=request.user).update(is_read=True, read_at=timezone.now())

        conversation.patient_unread_count = 0
        conversation.save(update_fields=['patient_unread_count'])

        return Response({'status': 'ok'})


# ─────────────────────────────────────────────
# Feature B: Doctor-Patient Messaging (Doktor)
# ─────────────────────────────────────────────

class DoctorConversationViewSet(viewsets.ModelViewSet):
    """Doktor tarafli mesajlasma konusmalari."""
    permission_classes = [permissions.IsAuthenticated, IsDoctor]
    http_method_names = ['get', 'post']

    def get_queryset(self):
        return Conversation.objects.filter(
            doctor=self.request.user,
        ).select_related('patient').exclude(status='archived')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ConversationDetailSerializer
        return ConversationListSerializer

    @action(detail=True, methods=['post'], url_path='send')
    def send_message(self, request, pk=None):
        """Doktor mesaj gonder."""
        conversation = self.get_object()

        if conversation.status != 'active':
            return Response(
                {'error': 'Bu konusma kapatilmis.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        msg = DirectMessage.objects.create(
            conversation=conversation,
            sender=request.user,
            content=serializer.validated_data['content'],
        )

        conversation.last_message_at = timezone.now()
        conversation.patient_unread_count += 1
        conversation.save(update_fields=['last_message_at', 'patient_unread_count'])

        _notify_new_message(conversation.patient, request.user, conversation)

        return Response(DirectMessageSerializer(msg).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='close')
    def close_conversation(self, request, pk=None):
        """Konusmayi kapat."""
        conversation = self.get_object()
        conversation.status = 'closed'
        conversation.save(update_fields=['status'])
        return Response({'status': 'closed'})

    @action(detail=True, methods=['post'], url_path='mark-read')
    def mark_read(self, request, pk=None):
        """Okunmamis mesajlari okundu isaretle."""
        conversation = self.get_object()

        DirectMessage.objects.filter(
            conversation=conversation,
            is_read=False,
        ).exclude(sender=request.user).update(is_read=True, read_at=timezone.now())

        conversation.doctor_unread_count = 0
        conversation.save(update_fields=['doctor_unread_count'])

        return Response({'status': 'ok'})


class DoctorConversationStatsView(generics.GenericAPIView):
    """Doktor mesajlasma istatistikleri."""
    permission_classes = [permissions.IsAuthenticated, IsDoctor]

    def get(self, request):
        conversations = Conversation.objects.filter(doctor=request.user)
        active = conversations.filter(status='active').count()
        total_unread = sum(
            c.doctor_unread_count
            for c in conversations.filter(status='active')
        )
        return Response({
            'active_conversations': active,
            'total_unread': total_unread,
            'total_conversations': conversations.count(),
        })


# ─── Helpers ───

def _notify_new_message(recipient, sender, conversation):
    """Yeni mesaj bildirimi olustur."""
    try:
        from apps.notifications.models import Notification

        sender_name = sender.get_full_name()
        if sender.role == 'doctor':
            sender_name = f"Dr. {sender_name}"

        Notification.objects.create(
            recipient=recipient,
            notification_type='info',
            title_tr=f'{sender_name} yeni mesaj gonderdi',
            title_en=f'New message from {sender_name}',
            message_tr=f'{conversation.subject or "Konusma"}: yeni bir mesajiniz var.',
            message_en=f'{conversation.subject or "Conversation"}: you have a new message.',
            action_url=f'/{"doctor" if recipient.role == "doctor" else "patient"}/messages',
            metadata={'conversation_id': str(conversation.id), 'sender_id': str(sender.id)},
        )

        # Async email bildirimi
        from apps.notifications.tasks import send_notification_email_async
        send_notification_email_async.delay(
            recipient.email,
            f'{sender_name} - Yeni Mesaj',
            f'{sender_name} size bir mesaj gonderdi. Platforma girerek goruntuleyebilirsiniz.',
        )
    except Exception as e:
        logger.warning(f"Message notification error: {e}")
