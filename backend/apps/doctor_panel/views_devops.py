"""
DevOps Agent API endpoint.

POST /api/v1/doctor/devops/generate/   - Kod uretme
POST /api/v1/doctor/devops/review/     - Kod review
"""

import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.accounts.permissions import IsDoctor
from apps.common.throttles import AIAgentThrottle

logger = logging.getLogger(__name__)


class DevOpsGenerateView(APIView):
    """DevOps Agent ile kod uretme."""
    permission_classes = [IsAuthenticated, IsDoctor]
    throttle_classes = [AIAgentThrottle]

    def post(self, request):
        task = request.data.get('task', '').strip()
        task_type = request.data.get('task_type', 'create_model')
        context = request.data.get('context', '')
        target_app = request.data.get('target_app', '')

        if not task:
            return Response(
                {'error': 'Gorev (task) zorunludur.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        valid_types = ['create_model', 'create_view', 'create_serializer',
                       'create_test', 'create_page', 'refactor', 'analyze']
        if task_type not in valid_types:
            return Response(
                {'error': f'Gecersiz task_type. Desteklenen: {valid_types}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from services.base_agent import BaseAgent
        original_is_enabled = BaseAgent.is_enabled
        BaseAgent.is_enabled = lambda self: True

        try:
            from services.agents.devops_agent import DevOpsAgent
            agent = DevOpsAgent()
            result = agent.execute({
                'task': task,
                'task_type': task_type,
                'context': context,
                'target_app': target_app,
            })

            logger.info(f"[DEVOPS] Generate: type={task_type}, user={request.user.email}")

            return Response({
                'success': True,
                'task_type': task_type,
                'result': result,
            })
        except Exception as e:
            logger.error(f"[DEVOPS] Generate error: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        finally:
            BaseAgent.is_enabled = original_is_enabled


class DevOpsReviewView(APIView):
    """DevOps Agent ile kod review."""
    permission_classes = [IsAuthenticated, IsDoctor]
    throttle_classes = [AIAgentThrottle]

    def post(self, request):
        task = request.data.get('task', 'Kodu incele ve kalite raporu olustur')
        file_content = request.data.get('file_content', '').strip()

        if not file_content:
            return Response(
                {'error': 'Kod icerigi (file_content) zorunludur.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from services.base_agent import BaseAgent
        original_is_enabled = BaseAgent.is_enabled
        BaseAgent.is_enabled = lambda self: True

        try:
            from services.agents.devops_agent import DevOpsAgent
            agent = DevOpsAgent()
            result = agent.execute({
                'task': task,
                'task_type': 'review',
                'file_content': file_content,
            })

            logger.info(f"[DEVOPS] Review: user={request.user.email}")

            return Response({
                'success': True,
                'result': result,
            })
        except Exception as e:
            logger.error(f"[DEVOPS] Review error: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        finally:
            BaseAgent.is_enabled = original_is_enabled
