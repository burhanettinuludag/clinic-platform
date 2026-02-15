#!/usr/bin/env python3
"""
DevOps/Code Agent Uctan Uca Test.

Calistirma:
    cd backend
    DJANGO_SETTINGS_MODULE=config.settings.development python3 tests/test_devops_agent_e2e.py

Test senaryolari:
    1. Model olusturma (mock LLM)
    2. View olusturma
    3. Serializer olusturma
    4. Test dosyasi olusturma
    5. Next.js page olusturma
    6. Kod review modu
    7. Output validation - basarili
    8. Output validation - bos task hatasi
    9. Output validation - parse hatasi
    10. Prompt build dogrulama
    11. Markdown wrapped JSON parse
    12. BaseAgent.run entegrasyonu
    13. FeatureFlag disabled -> skip
    14. Gercek LLM testi (opsiyonel)
"""

import os
import sys
import json
import logging
from unittest.mock import patch, MagicMock

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django
django.setup()

from services.agents.devops_agent import DevOpsAgent
from services.base_agent import BaseAgent
from services.llm_client import LLMResponse

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# MOCK DATA
# ─────────────────────────────────────────────

MOCK_MODEL_RESPONSE = json.dumps({
    "task_type": "create_model",
    "files": [
        {
            "path": "backend/apps/content/models.py",
            "action": "append",
            "content": "class FAQ(TimeStampedModel):\n    question_tr = models.CharField(max_length=500)\n    answer_tr = models.TextField()\n    category = models.ForeignKey(ContentCategory, on_delete=models.SET_NULL, null=True)\n    is_active = models.BooleanField(default=True)\n    order = models.PositiveIntegerField(default=0)\n\n    class Meta:\n        ordering = ['order']\n\n    def __str__(self):\n        return self.question_tr[:80]",
            "description": "FAQ modeli - SSS icin"
        }
    ],
    "migration_needed": True,
    "tests": ["test_faq_model.py"],
    "notes": "Migration olusturmayi unutma: python manage.py makemigrations content"
})

MOCK_VIEW_RESPONSE = json.dumps({
    "task_type": "create_view",
    "files": [
        {
            "path": "backend/apps/content/views.py",
            "action": "append",
            "content": "class FAQListView(generics.ListAPIView):\n    serializer_class = FAQSerializer\n    permission_classes = [AllowAny]\n    def get_queryset(self):\n        return FAQ.objects.filter(is_active=True).order_by('order')",
            "description": "Public FAQ listesi"
        }
    ],
    "migration_needed": False,
    "tests": ["test_faq_views.py"],
    "notes": "URL eklemeyi unutma"
})

MOCK_REVIEW_RESPONSE = json.dumps({
    "score": 72,
    "issues": [
        {"severity": "warning", "line": 15, "message": "N+1 query potansiyeli", "suggestion": "select_related('category') ekle"},
        {"severity": "info", "line": 8, "message": "Docstring eksik", "suggestion": "Class docstring ekle"}
    ],
    "summary": "Genel olarak iyi, N+1 query ve dokumantasyon iyilestirmesi gerekli"
})

MOCK_PAGE_RESPONSE = json.dumps({
    "task_type": "create_page",
    "files": [
        {
            "path": "frontend/src/app/[locale]/faq/page.tsx",
            "action": "create",
            "content": "'use client';\nimport { useQuery } from '@tanstack/react-query';\nexport default function FAQPage() { return <div>FAQ</div>; }",
            "description": "FAQ sayfasi"
        }
    ],
    "migration_needed": False,
    "tests": [],
    "notes": "React Query hook ayri dosyaya cikarilabilir"
})

def make_mock_response(content):
    return LLMResponse(
        content=content,
        provider='groq',
        model='llama-3.3-70b-versatile',
        tokens_used=500,
        duration_ms=800,
    )

# ─────────────────────────────────────────────
# TEST RUNNER
# ─────────────────────────────────────────────

results = []

def run_test(name, fn):
    try:
        fn()
        results.append(('PASS', name))
        logger.info(f'PASS: {name}')
    except Exception as e:
        results.append(('FAIL', name))
        logger.error(f'FAIL: {name} -> {e}')

# ─────────────────────────────────────────────
# TEST 1: Model olusturma (mock LLM)
# ─────────────────────────────────────────────
def test_create_model():
    agent = DevOpsAgent()
    with patch.object(agent, 'llm_call', return_value=make_mock_response(MOCK_MODEL_RESPONSE)):
        result = agent.execute({
            'task': 'FAQ modeli olustur: soru, cevap, kategori, siralama',
            'task_type': 'create_model',
            'target_app': 'content',
        })
    assert 'files' in result, 'files alani eksik'
    assert len(result['files']) > 0, 'Dosya listesi bos'
    assert result['files'][0]['path'].endswith('.py'), 'Dosya uzantisi yanlis'
    assert result['migration_needed'] == True, 'Migration gerekli olmali'
    assert 'FAQ' in result['files'][0]['content'], 'Model adi icerikte yok'

run_test('1. Model olusturma (mock LLM)', test_create_model)

# ─────────────────────────────────────────────
# TEST 2: View olusturma
# ─────────────────────────────────────────────
def test_create_view():
    agent = DevOpsAgent()
    with patch.object(agent, 'llm_call', return_value=make_mock_response(MOCK_VIEW_RESPONSE)):
        result = agent.execute({
            'task': 'FAQ public list endpoint olustur',
            'task_type': 'create_view',
            'target_app': 'content',
        })
    assert result['task_type'] == 'create_view'
    assert result['migration_needed'] == False
    assert 'FAQListView' in result['files'][0]['content']

run_test('2. View olusturma', test_create_view)

# ─────────────────────────────────────────────
# TEST 3: Kod review modu
# ─────────────────────────────────────────────
def test_review_mode():
    agent = DevOpsAgent()
    with patch.object(agent, 'llm_call', return_value=make_mock_response(MOCK_REVIEW_RESPONSE)):
        result = agent.execute({
            'task': 'Bu kodu incele',
            'task_type': 'review',
            'file_content': 'class MyView(APIView):\n    def get(self, request):\n        return Response(Article.objects.all())',
        })
    assert 'score' in result, 'score alani eksik'
    assert result['score'] == 72
    assert len(result['issues']) == 2
    assert result['issues'][0]['severity'] == 'warning'

run_test('3. Kod review modu', test_review_mode)

# ─────────────────────────────────────────────
# TEST 4: Next.js page olusturma
# ─────────────────────────────────────────────
def test_create_page():
    agent = DevOpsAgent()
    with patch.object(agent, 'llm_call', return_value=make_mock_response(MOCK_PAGE_RESPONSE)):
        result = agent.execute({
            'task': 'FAQ sayfasi olustur',
            'task_type': 'create_page',
        })
    assert result['task_type'] == 'create_page'
    assert 'page.tsx' in result['files'][0]['path']
    assert 'use client' in result['files'][0]['content']

run_test('4. Next.js page olusturma', test_create_page)

# ─────────────────────────────────────────────
# TEST 5: Bos task hatasi
# ─────────────────────────────────────────────
def test_empty_task():
    agent = DevOpsAgent()
    result = agent.execute({'task': '', 'task_type': 'create_model'})
    assert 'error' in result

run_test('5. Bos task hatasi', test_empty_task)

# ─────────────────────────────────────────────
# TEST 6: Review - file_content eksik hatasi
# ─────────────────────────────────────────────
def test_review_no_content():
    agent = DevOpsAgent()
    result = agent.execute({'task': 'Incele', 'task_type': 'review', 'file_content': ''})
    assert 'error' in result

run_test('6. Review file_content eksik hatasi', test_review_no_content)

# ─────────────────────────────────────────────
# TEST 7: Parse hatasi - broken JSON
# ─────────────────────────────────────────────
def test_broken_json():
    agent = DevOpsAgent()
    with patch.object(agent, 'llm_call', return_value=make_mock_response('bu json degil {')):
        result = agent.execute({'task': 'Bir sey yap', 'task_type': 'create_model'})
    assert result.get('parse_error') == True

run_test('7. Parse hatasi - broken JSON', test_broken_json)

# ─────────────────────────────────────────────
# TEST 8: Markdown wrapped JSON
# ─────────────────────────────────────────────
def test_markdown_json():
    agent = DevOpsAgent()
    wrapped = '```json\n' + MOCK_MODEL_RESPONSE + '\n```'
    with patch.object(agent, 'llm_call', return_value=make_mock_response(wrapped)):
        result = agent.execute({'task': 'Model olustur', 'task_type': 'create_model'})
    assert 'files' in result, 'Markdown wrapped JSON parse edilemedi'

run_test('8. Markdown wrapped JSON parse', test_markdown_json)

# ─────────────────────────────────────────────
# TEST 9: Prompt build dogrulama
# ─────────────────────────────────────────────
def test_prompt_build():
    agent = DevOpsAgent()
    prompt = agent._build_prompt(
        task='Test modeli olustur',
        task_type='create_model',
        context='Mevcut Article modeli var',
        target_app='content',
    )
    assert 'Test modeli olustur' in prompt
    assert 'create_model' in prompt
    assert 'content' in prompt
    assert 'Mevcut Article modeli var' in prompt
    assert 'TimeStampedModel' in prompt  # type hint

run_test('9. Prompt build dogrulama', test_prompt_build)

# ─────────────────────────────────────────────
# TEST 10: Context truncation (3000 char)
# ─────────────────────────────────────────────
def test_context_truncation():
    agent = DevOpsAgent()
    long_ctx = 'x' * 5000
    prompt = agent._build_prompt('task', 'create_model', long_ctx, '')
    assert len(prompt) < 5000, 'Context truncate edilmemis'

run_test('10. Context 3000 char truncation', test_context_truncation)

# ─────────────────────────────────────────────
# TEST 11: validate_output basarili
# ─────────────────────────────────────────────
def test_validate_success():
    agent = DevOpsAgent()
    err = agent.validate_output({'files': [], 'task_type': 'create_model'})
    assert err is None

run_test('11. validate_output basarili', test_validate_success)

# ─────────────────────────────────────────────
# TEST 12: validate_output error
# ─────────────────────────────────────────────
def test_validate_error():
    agent = DevOpsAgent()
    err = agent.validate_output({'error': 'task alani zorunlu'})
    assert err is not None

run_test('12. validate_output error', test_validate_error)

# ─────────────────────────────────────────────
# TEST 13: validate_output parse_error
# ─────────────────────────────────────────────
def test_validate_parse_error():
    agent = DevOpsAgent()
    err = agent.validate_output({'parse_error': True, 'raw_content': 'bozuk'})
    assert err is not None

run_test('13. validate_output parse_error', test_validate_parse_error)

# ─────────────────────────────────────────────
# TEST 14: BaseAgent.run entegrasyonu
# ─────────────────────────────────────────────
def test_base_agent_run():
    agent = DevOpsAgent()
    with patch.object(agent, 'llm_call', return_value=make_mock_response(MOCK_MODEL_RESPONSE)):
        with patch('services.base_agent.FeatureFlag') as mock_ff:
            mock_ff.is_enabled.return_value = True
            result = agent.run({'task': 'FAQ olustur', 'task_type': 'create_model'})
    assert result.success == True
    assert 'files' in result.data

run_test('14. BaseAgent.run entegrasyonu', test_base_agent_run)

# ─────────────────────────────────────────────
# TEST 15: FeatureFlag disabled -> skip
# ─────────────────────────────────────────────
def test_feature_flag_disabled():
    agent = DevOpsAgent()
    with patch('services.base_agent.FeatureFlag') as mock_ff:
        mock_ff.is_enabled.return_value = False
        result = agent.run({'task': 'bir sey', 'task_type': 'create_model'})
    assert result.success == False or result.skipped == True

run_test('15. FeatureFlag disabled -> skip', test_feature_flag_disabled)

# ─────────────────────────────────────────────
# TEST 16: Gercek LLM testi (opsiyonel)
# ─────────────────────────────────────────────
def test_real_llm():
    api_key = os.environ.get('GROQ_API_KEY', '')
    if not api_key:
        logger.info('SKIP: GROQ_API_KEY bulunamadi')
        return
    agent = DevOpsAgent()
    result = agent.execute({
        'task': 'Basit bir HealthCheck model olustur: status, checked_at, response_time_ms',
        'task_type': 'create_model',
        'target_app': 'common',
    })
    assert 'files' in result or 'error' not in result, f'Gercek LLM hatasi: {result}'
    logger.info(f'Gercek LLM sonucu: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}')

run_test('16. Gercek LLM testi (opsiyonel)', test_real_llm)

# ─────────────────────────────────────────────
# SONUC
# ─────────────────────────────────────────────
print('\n' + '=' * 50)
passed = sum(1 for r, _ in results if r == 'PASS')
total = len(results)
print(f'SONUC: {passed}/{total} test basarili')
for status, name in results:
    icon = 'v' if status == 'PASS' else 'X'
    print(f'  [{icon}] {name}')

if passed < total:
    sys.exit(1)
