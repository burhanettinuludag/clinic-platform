"""
DevOps/Code Agent.

Kod uretme, analiz etme ve refactor onerileri:
- Django model, view, serializer, URL olusturma
- React hook, page, component olusturma
- Kod review ve kalite analizi
- Test yazma
- Migration onerisi

Content Agent'tan farkli olarak, tıbbi icerik degil yazilim kodu uretir.
"""

import json
import logging
import re
from typing import Optional

from services.base_agent import BaseAgent
from services.prompts.devops_prompts import DEVOPS_SYSTEM_PROMPT, CODE_REVIEW_PROMPT

logger = logging.getLogger(__name__)


class DevOpsAgent(BaseAgent):
    """Platform icin kod ureten ve analiz eden ajan."""

    name = 'devops_agent'
    task_type = 'generate_code'
    system_prompt = DEVOPS_SYSTEM_PROMPT
    feature_flag_key = 'agent_devops'
    temperature = 0.2
    max_tokens = 4000

    def execute(self, input_data: dict) -> dict:
        """
        Kod uretme veya analiz.

        Input:
            task: str - Gorev aciklamasi
            task_type: str - create_model|create_view|create_serializer|
                             create_test|create_page|refactor|analyze|review
            context: str - Ek baghlam (mevcut kod, model yapisi vb.)
            target_app: str - Hedef Django app (opsiyonel)
            file_content: str - Review/refactor icin mevcut dosya icerigi

        Output:
            task_type, files[], migration_needed, tests[], notes
        """
        task = input_data.get('task', '')
        task_type = input_data.get('task_type', 'create_model')
        context = input_data.get('context', '')
        target_app = input_data.get('target_app', '')
        file_content = input_data.get('file_content', '')

        if not task:
            return {'error': 'task alani zorunlu'}

        # Review modu icin farkli prompt
        if task_type == 'review':
            return self._run_review(task, file_content)

        prompt = self._build_prompt(task, task_type, context, target_app)
        response = self.llm_call(prompt)
        result = self._parse_response(response.content)

        result['devops_provider'] = response.provider
        result['devops_tokens'] = response.tokens_used
        return result

    def _build_prompt(self, task, task_type, context, target_app):
        """Kod uretme prompt'u."""
        parts = [f"GOREV: {task}", f"GOREV TIPI: {task_type}"]

        if target_app:
            parts.append(f"HEDEF APP: {target_app}")

        if context:
            ctx_preview = context[:3000] if len(context) > 3000 else context
            parts.append(f"BAGHLAM:\n{ctx_preview}")

        type_hints = {
            'create_model': 'Django model olustur. TimeStampedModel miras al, UUID pk, Meta class, __str__ ekle.',
            'create_view': 'DRF view olustur. Uygun permission, serializer, queryset tanimla.',
            'create_serializer': 'DRF serializer olustur. SerializerMethodField, validate, create/update ekle.',
            'create_test': 'Test dosyasi olustur. Mock LLM, factory_boy pattern, assert kontrolleri.',
            'create_page': 'Next.js page olustur. use client, React Query hook, Tailwind styling.',
            'refactor': 'Mevcut kodu refactor et. DRY, SOLID, performance iyilestirmeleri.',
            'analyze': 'Kodu analiz et. Eksikleri, riskleri ve iyilestirme onerileri ver.',
        }
        if task_type in type_hints:
            parts.append(f"IPUCU: {type_hints[task_type]}")

        return '\n\n'.join(parts)

    def _run_review(self, task, file_content):
        """Kod review modu."""
        if not file_content:
            return {'error': 'review icin file_content zorunlu'}

        prompt = f"""GOREV: {task}

KOD:
```
{file_content[:5000]}
```

Bu kodu incele ve kalite raporu olustur."""

        response = self.llm_call(prompt, system_prompt=CODE_REVIEW_PROMPT)
        result = self._parse_response(response.content)
        result['review_provider'] = response.provider
        result['review_tokens'] = response.tokens_used
        return result

    def _parse_response(self, content: str) -> dict:
        """LLM yanitini parse et."""
        cleaned = content.strip()
        # Markdown code block temizle
        cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
        cleaned = re.sub(r'\s*```$', '', cleaned)

        match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

        logger.warning('DevOpsAgent: JSON parse hatasi')
        return {'parse_error': True, 'raw_content': content[:500]}

    def validate_output(self, output: dict) -> Optional[str]:
        """Cikti dogrulama."""
        if output.get('error'):
            return output['error']
        if output.get('parse_error'):
            return 'DevOps ciktisi parse edilemedi'
        return None
