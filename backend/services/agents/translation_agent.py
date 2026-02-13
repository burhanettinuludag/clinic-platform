"""
Cevirmen Ajan - TR -> EN tibbi icerik cevirisi.

Pipeline'da Legal Agent'tan sonra calisir.
Content Agent'in urettigi Turkce icerigi Ingilizce'ye cevirir.
"""

import json
import logging
import re
from typing import Optional

from services.base_agent import BaseAgent
from services.prompts.translation_prompts import TRANSLATION_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class TranslationAgent(BaseAgent):
    """Turkce saglik icerigini Ingilizce'ye ceviren ajan."""

    name = 'translation_agent'
    system_prompt = TRANSLATION_SYSTEM_PROMPT
    feature_flag_key = 'agent_translation'
    temperature = 0.2
    max_tokens = 3000

    def execute(self, input_data: dict) -> dict:
        """
        Turkce icerigi Ingilizce'ye cevir.

        Input: title_tr, body_tr, excerpt_tr, module
        Output: title_en, body_en, excerpt_en + SEO EN alanlari
        """
        title_tr = input_data.get('title_tr', '')
        body_tr = input_data.get('body_tr', '')
        excerpt_tr = input_data.get('excerpt_tr', '')
        module = input_data.get('module', 'general')

        if not body_tr:
            return {**input_data, 'translation_error': 'Cevirilecek icerik (body_tr) bos'}

        # Icerik cok uzunsa parcala: sadece baslik + ozet + body'nin ilk 2000 karakteri
        body_short = body_tr[:2000] if len(body_tr) > 2000 else body_tr

        prompt = self._build_prompt(title_tr, body_short, excerpt_tr, module)
        response = self.llm_call(prompt)
        translation_data = self._parse_response(response.content)

        result = {**input_data}

        if translation_data.get('title_en'):
            result['title_en'] = translation_data['title_en']
        if translation_data.get('body_en'):
            result['body_en'] = translation_data['body_en']
        if translation_data.get('excerpt_en'):
            result['excerpt_en'] = translation_data['excerpt_en']
        if not result.get('seo_title_en') and translation_data.get('seo_title_en'):
            result['seo_title_en'] = translation_data['seo_title_en']
        if not result.get('seo_description_en') and translation_data.get('seo_description_en'):
            result['seo_description_en'] = translation_data['seo_description_en']

        result['translation_provider'] = response.provider
        result['translation_tokens'] = response.tokens_used
        return result

    def _build_prompt(self, title_tr, body_tr, excerpt_tr, module):
        """Ceviri prompt'u."""
        module_context = {
            'migraine': 'migraine / headache neurology',
            'epilepsy': 'epilepsy / seizure disorders',
            'dementia': 'dementia / Alzheimer disease',
            'wellness': 'wellness / healthy living',
            'general': 'general neurology',
        }
        context = module_context.get(module, 'neurology')

        return f"""Translate the following Turkish medical content to English.

MEDICAL FIELD: {context}

TURKISH TITLE: {title_tr}

TURKISH SUMMARY: {excerpt_tr}

TURKISH CONTENT:
{body_tr}

RULES:
1. Translate medical terms correctly
2. Keep the informational tone
3. Translate the disclaimer too
4. Keep Markdown formatting
5. Write natural English

OUTPUT FORMAT (JSON):
{{
    "title_en": "English title",
    "body_en": "Full English content in Markdown",
    "excerpt_en": "2-3 sentence English summary",
    "seo_title_en": "SEO title max 60 chars",
    "seo_description_en": "Meta description max 160 chars"
}}

Return ONLY JSON, nothing else."""

    def _parse_response(self, content: str) -> dict:
        """LLM yanitini parse et - robust parser."""
        cleaned = content.strip()

        # 1. Dogrudan parse
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # 2. Backtick temizle
        cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
        cleaned = re.sub(r'\s*```$', '', cleaned)
        cleaned = cleaned.strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # 3. { } blogu bul
        match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if match:
            raw = match.group(0)
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                pass

            # 4. Key-value extraction
            result = {}
            for key in ['title_en', 'excerpt_en', 'seo_title_en', 'seo_description_en']:
                km = re.search(r'"' + key + r'"\s*:\s*"((?:[^"\\]|\\.)*)"', raw)
                if km:
                    result[key] = km.group(1).replace('\\n', '\n').replace('\\"', '"')

            # body_en ozel: multiline
            bm = re.search(
                r'"body_en"\s*:\s*"(.*?)"(?:\s*,\s*"(?:excerpt|seo_)|\s*\})',
                raw,
                re.DOTALL
            )
            if bm:
                result['body_en'] = bm.group(1).replace('\\n', '\n').replace('\\"', '"')

            if result.get('title_en') or result.get('body_en'):
                return result

        logger.warning('TranslationAgent: JSON parse hatasi')
        return {'translation_parse_error': True}

    def validate_output(self, output: dict) -> Optional[str]:
        """Cikti dogrulama."""
        if output.get('translation_error'):
            return output['translation_error']
        if output.get('translation_parse_error'):
            return "Ceviri ciktisi parse edilemedi"
        if not output.get('body_en') and not output.get('translation_parse_error'):
            return "Ingilizce icerik (body_en) bos"
        return None