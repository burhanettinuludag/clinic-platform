"""
Icerik uretim API endpoint'i.
Doctor panel'den cagirilir, pipeline'i tetikler.

POST /api/v1/doctor/generate-content/
GET  /api/v1/doctor/generated-content/  (taslak listesi)
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.accounts.permissions import IsDoctor
from apps.common.throttles import AIAgentThrottle


class GenerateContentView(APIView):
    """Icerik uretim pipeline'ini tetikler."""
    permission_classes = [IsAuthenticated, IsDoctor]
    throttle_classes = [AIAgentThrottle]

    def post(self, request):
        topic = request.data.get('topic', '').strip()
        module = request.data.get('module', 'general')
        audience = request.data.get('audience', 'patient')
        content_type = request.data.get('content_type', 'blog')
        tone = request.data.get('tone', 'friendly')

        if not topic:
            return Response(
                {'error': 'Konu (topic) zorunludur.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # FeatureFlag bypass - ajanları dogrudan calistir
        from services.base_agent import BaseAgent
        original_is_enabled = BaseAgent.is_enabled
        BaseAgent.is_enabled = lambda self: True

        try:
            from services.orchestrator import orchestrator
            import services.agents  # noqa: F401

            result = orchestrator.run_chain(
                'publish_article',
                input_data={
                    'topic': topic,
                    'module': module,
                    'audience': audience,
                    'content_type': content_type,
                    'tone': tone,
                },
                steps=['content_agent', 'seo_agent', 'legal_agent'],
                triggered_by=request.user,
            )

            if result.success:
                # Article modeline draft olarak kaydet
                article = self._save_as_draft(result.final_data, request.user)

                return Response({
                    'success': True,
                    'article_id': str(article.id) if article else None,
                    'title': result.final_data.get('title_tr', ''),
                    'seo_title': result.final_data.get('seo_title_tr', ''),
                    'legal_approved': result.final_data.get('legal_approved', False),
                    'legal_score': result.final_data.get('legal_score', 0),
                    'legal_issues': result.final_data.get('legal_issues', []),
                    'keywords': result.final_data.get('keywords_tr', []),
                    'steps_completed': result.steps_completed,
                    'duration_ms': result.total_duration_ms,
                })
            else:
                return Response({
                    'success': False,
                    'error': result.error,
                    'steps_completed': result.steps_completed,
                    'steps_failed': result.steps_failed,
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        finally:
            BaseAgent.is_enabled = original_is_enabled

    def _save_as_draft(self, data, author):
        """Pipeline sonucunu Article modeline draft olarak kaydet."""
        try:
            from apps.content.models import Article
            from django.utils.text import slugify
            from django.utils import timezone
            import uuid

            title_tr = data.get('title_tr', 'Basliksiz Icerik')
            slug_base = slugify(title_tr[:80]) or f'icerik-{uuid.uuid4().hex[:8]}'

            # Slug benzersizligi
            slug = slug_base
            counter = 1
            while Article.objects.filter(slug=slug).exists():
                slug = f'{slug_base}-{counter}'
                counter += 1

            article = Article.objects.create(
                slug=slug,
                title_tr=title_tr,
                title_en=data.get('seo_title_en', title_tr),
                body_tr=data.get('body_tr', ''),
                body_en='',  # Translation agent sonra dolduracak
                excerpt_tr=data.get('excerpt_tr', ''),
                excerpt_en='',
                author=author,
                status='draft',
                seo_title_tr=data.get('seo_title_tr', ''),
                seo_title_en=data.get('seo_title_en', ''),
                seo_description_tr=data.get('seo_description_tr', ''),
                seo_description_en=data.get('seo_description_en', ''),
            )
            return article
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Article kaydetme hatasi: {e}")
            return None


class GeneratedContentListView(APIView):
    """Hekim tarafindan uretilen taslak icerikleri listeler."""
    permission_classes = [IsAuthenticated, IsDoctor]

    def get(self, request):
        from apps.content.models import Article

        drafts = Article.objects.filter(
            author=request.user,
            status='draft',
        ).order_by('-created_at')[:20]

        data = [
            {
                'id': str(d.id),
                'title': d.title_tr,
                'excerpt': d.excerpt_tr,
                'seo_title': d.seo_title_tr,
                'created_at': d.created_at.isoformat(),
                'status': d.status,
            }
            for d in drafts
        ]
        return Response(data)
