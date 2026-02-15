"""
Icerik yayin akisi bildirim servisi.
Durum gecislerinde otomatik bildirim gonderir.
"""
import logging
from django.db.models import Q
from apps.notifications.models import Notification
from apps.accounts.models import CustomUser, DoctorAuthor

logger = logging.getLogger(__name__)

TEMPLATES = {
    'article_submitted': {
        'title_tr': 'Makaleniz incelemeye gonderildi',
        'title_en': 'Your article has been submitted for review',
        'message_tr': '"{title}" baslikli makaleniz inceleme kuyruğuna eklendi.',
        'message_en': 'Your article "{title}" has been added to the review queue.',
        'type': 'info',
    },
    'article_approved': {
        'title_tr': 'Makaleniz onaylandi',
        'title_en': 'Your article has been approved',
        'message_tr': '"{title}" baslikli makaleniz onaylandi ve yayina hazir.',
        'message_en': 'Your article "{title}" has been approved and is ready for publication.',
        'type': 'info',
    },
    'article_rejected': {
        'title_tr': 'Makaleniz duzeltme istiyor',
        'title_en': 'Your article needs revision',
        'message_tr': '"{title}" icin duzeltme istendi. Geri bildirim: {feedback}',
        'message_en': 'Revision requested for "{title}". Feedback: {feedback}',
        'type': 'alert',
    },
    'article_published': {
        'title_tr': 'Makaleniz yayinda!',
        'title_en': 'Your article is now live!',
        'message_tr': '"{title}" baslikli makaleniz basariyla yayinlandi.',
        'message_en': 'Your article "{title}" has been published successfully.',
        'type': 'info',
    },
    'article_archived': {
        'title_tr': 'Makaleniz arsivlendi',
        'title_en': 'Your article has been archived',
        'message_tr': '"{title}" baslikli makaleniz arsivlendi.',
        'message_en': 'Your article "{title}" has been archived.',
        'type': 'info',
    },
    'news_submitted': {
        'title_tr': 'Haberiniz incelemeye gonderildi',
        'title_en': 'Your news has been submitted for review',
        'message_tr': '"{title}" baslikli haberiniz inceleme kuyruğuna eklendi.',
        'message_en': 'Your news "{title}" has been added to the review queue.',
        'type': 'info',
    },
    'news_approved': {
        'title_tr': 'Haberiniz onaylandi',
        'title_en': 'Your news has been approved',
        'message_tr': '"{title}" baslikli haberiniz onaylandi.',
        'message_en': 'Your news "{title}" has been approved.',
        'type': 'info',
    },
    'news_rejected': {
        'title_tr': 'Haberiniz duzeltme istiyor',
        'title_en': 'Your news needs revision',
        'message_tr': '"{title}" icin duzeltme istendi. Geri bildirim: {feedback}',
        'message_en': 'Revision requested for "{title}". Feedback: {feedback}',
        'type': 'alert',
    },
    'news_published': {
        'title_tr': 'Haberiniz yayinda!',
        'title_en': 'Your news is now live!',
        'message_tr': '"{title}" baslikli haberiniz yayinlandi.',
        'message_en': 'Your news "{title}" has been published.',
        'type': 'info',
    },
    'news_auto_published': {
        'title_tr': 'Haberiniz otomatik yayinlandi',
        'title_en': 'Your news was auto-published',
        'message_tr': '"{title}" kidemli yazar yetkinizle otomatik yayinlandi.',
        'message_en': '"{title}" was auto-published with your senior author privileges.',
        'type': 'info',
    },
    'editor_new_submission': {
        'title_tr': 'Yeni icerik incelemede',
        'title_en': 'New content awaiting review',
        'message_tr': '{author_name} tarafindan "{title}" inceleme bekliyor.',
        'message_en': '"{title}" by {author_name} is awaiting review.',
        'type': 'info',
    },
    'pipeline_completed': {
        'title_tr': 'Pipeline tamamlandi',
        'title_en': 'Pipeline completed',
        'message_tr': '"{title}" icin {pipeline_name} pipeline tamamlandi. Skor: {score}',
        'message_en': '{pipeline_name} pipeline completed for "{title}". Score: {score}',
        'type': 'info',
    },
    'pipeline_failed': {
        'title_tr': 'Pipeline hatasi',
        'title_en': 'Pipeline failed',
        'message_tr': '"{title}" icin {pipeline_name} pipeline hatali tamamlandi.',
        'message_en': '{pipeline_name} pipeline failed for "{title}".',
        'type': 'alert',
    },
}


def _create_notification(recipient, template_key, context, action_url='', metadata=None):
    template = TEMPLATES.get(template_key)
    if not template:
        return None
    try:
        notification = Notification.objects.create(
            recipient=recipient,
            notification_type=template['type'],
            title_tr=template['title_tr'].format(**context),
            title_en=template['title_en'].format(**context),
            message_tr=template['message_tr'].format(**context),
            message_en=template['message_en'].format(**context),
            action_url=action_url,
            metadata=metadata or {},
        )
        # Email gonder
        try:
            from apps.notifications.email_service import send_notification_email
            send_notification_email(notification)
        except Exception:
            pass
        return notification
    except Exception as e:
        logger.error(f"Bildirim hatasi: {e}")
        return None


def _get_editors():
    editors = []
    admins = CustomUser.objects.filter(Q(role='admin') | Q(is_staff=True), is_active=True)
    editors.extend(list(admins))
    editor_authors = DoctorAuthor.objects.filter(author_level__gte=4, is_active=True).select_related('doctor__user')
    for a in editor_authors:
        if a.doctor.user not in editors:
            editors.append(a.doctor.user)
    return editors


def notify_article_transition(article, old_status, new_status, changed_by=None, feedback=''):
    title = article.title_tr or article.title_en or 'Basliksiz'
    author_user = article.author
    ctx = {'title': title, 'feedback': feedback or '-', 'author_name': changed_by.get_full_name() if changed_by else ''}
    url = '/doctor/author'
    meta = {'article_id': str(article.id), 'old_status': old_status, 'new_status': new_status, 'content_type': 'article'}

    if author_user and changed_by != author_user:
        if new_status == 'published':
            _create_notification(author_user, 'article_published', ctx, url, meta)
        elif new_status == 'archived':
            _create_notification(author_user, 'article_archived', ctx, url, meta)
        elif new_status == 'approved':
            _create_notification(author_user, 'article_approved', ctx, url, meta)
        elif new_status == 'revision':
            _create_notification(author_user, 'article_rejected', ctx, url, meta)

    if old_status == 'draft' and new_status in ('review', 'published') and changed_by == author_user:
        _create_notification(author_user, 'article_submitted', ctx, url, meta)
        ctx['author_name'] = author_user.get_full_name() if author_user else 'Bilinmeyen'
        for editor in _get_editors():
            if editor != author_user:
                _create_notification(editor, 'editor_new_submission', ctx, '/doctor/editor/review-queue/', meta)


def notify_news_transition(news_article, old_status, new_status, changed_by=None, feedback='', auto_published=False):
    title = news_article.title_tr or news_article.title_en or 'Basliksiz'
    author_user = news_article.author.doctor.user if news_article.author else None
    ctx = {'title': title, 'feedback': feedback or '-', 'author_name': changed_by.get_full_name() if changed_by else ''}
    url = '/doctor/author'
    meta = {'news_id': str(news_article.id), 'old_status': old_status, 'new_status': new_status, 'content_type': 'news'}

    if author_user:
        if auto_published:
            _create_notification(author_user, 'news_auto_published', ctx, url, meta)
        elif new_status == 'published' and changed_by != author_user:
            _create_notification(author_user, 'news_published', ctx, url, meta)
        elif new_status == 'approved' and changed_by != author_user:
            _create_notification(author_user, 'news_approved', ctx, url, meta)
        elif new_status == 'revision' and changed_by != author_user:
            _create_notification(author_user, 'news_rejected', ctx, url, meta)

    if old_status in ('draft', 'revision') and new_status == 'review':
        if author_user:
            _create_notification(author_user, 'news_submitted', ctx, url, meta)
        ctx['author_name'] = author_user.get_full_name() if author_user else 'Bilinmeyen'
        for editor in _get_editors():
            if editor != author_user:
                _create_notification(editor, 'editor_new_submission', ctx, '/doctor/editor/review-queue/', meta)


def notify_pipeline_result(article_or_news, pipeline_name, success, score=None, user=None):
    title = getattr(article_or_news, 'title_tr', '') or 'Basliksiz'
    ctx = {'title': title, 'pipeline_name': pipeline_name, 'score': score or '-'}
    meta = {'pipeline': pipeline_name, 'success': success, 'score': score}
    if user:
        key = 'pipeline_completed' if success else 'pipeline_failed'
        _create_notification(user, key, ctx, '/doctor/author', meta)
