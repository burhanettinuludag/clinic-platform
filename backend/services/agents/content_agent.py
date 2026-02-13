"""
Icerik Uretici Ajan - Ilk ajan implementasyonu.

Blog yazisi, hasta bilgilendirme, egitim icerigi uretir.
Hekim onaylamadan yayinlanmaz (Article.status='draft').
"""

import json
import logging
from typing import Optional

from services.base_agent import BaseAgent
from services.prompts.content_prompts import CONTENT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class ContentAgent(BaseAgent):
    """Blog, bilgilendirme ve egitim icerigi ureten ajan."""

    name = 'content_agent'
    system_prompt = CONTENT_SYSTEM_PROMPT
    feature_flag_key = 'agent_content'
    temperature = 0.7
    max_tokens = 3000

    def execute(self, input_data: dict) -> dict:
        """
        Icerik uret.

        Input:
            topic: str - Konu (ornek: "Migren tetikleyicileri")
            module: str - Hastalik modulu (migraine/epilepsy/dementia/wellness/general)
            audience: str - Hedef kitle (patient/doctor/public) [default: patient]
            tone: str - Ton (formal/friendly) [default: friendly]
            content_type: str - Icerik tipi (blog/education/social) [default: blog]

        Output:
            title_tr, title_en, body_tr, excerpt_tr,
            seo_title_tr, seo_description_tr,
            suggested_category, content_type
        """
        topic = input_data.get('topic', '')
        module = input_data.get('module', 'general')
        audience = input_data.get('audience', 'patient')
        tone = input_data.get('tone', 'friendly')
        content_type = input_data.get('content_type', 'blog')

        if not topic:
            return {'error': 'Konu (topic) belirtilmedi'}

        prompt = self._build_prompt(topic, module, audience, tone, content_type)
        response = self.llm_call(prompt)

        # JSON parse
        parsed = self._parse_response(response.content)
        parsed['llm_provider'] = response.provider
        parsed['tokens_used'] = response.tokens_used
        parsed['content_type'] = content_type

        return parsed

    def _build_prompt(self, topic, module, audience, tone, content_type):
        """LLM'e gonderilecek prompt'u olustur."""
        audience_map = {
            'patient': 'hastalar (tibbi jargon kullanma, anlasilir yaz)',
            'doctor': 'hekimler (teknik dil kullanabilirsin)',
            'public': 'genel halk (saglik okuryazarligi dusuk olabilir)',
        }
        tone_map = {
            'formal': 'resmi ve akademik',
            'friendly': 'samimi ama bilimsel',
        }
        type_map = {
            'blog': 'blog yazisi (800-1200 kelime, giris-gelisme-sonuc)',
            'education': 'egitim icerigi (maddeler halinde, kisa paragraflar)',
            'social': 'sosyal medya postu (kisa, dikkat cekici, emoji kullanabilirsin)',
        }

        return f"""Asagidaki konuda Turkce bir {type_map.get(content_type, 'blog yazisi')} yaz.

Konu: {topic}
Hastalik modulu: {module}
Hedef kitle: {audience_map.get(audience, audience)}
Ton: {tone_map.get(tone, tone)}

KURALLAR:
- Tibbi oneri VERME, sadece bilgilendirme yap
- Her yaziinin sonuna "Bu yazi bilgilendirme amaclidir, hekiminize danisiniz" disclaimeri ekle
- Bilimsel kaynaklara atif yap (genel referans yeterli)
- Yanliis bilgi ICERME

CIKTI FORMATI (JSON):
{{
    "title_tr": "Turkce baslik",
    "body_tr": "Tam icerik (Markdown formati)",
    "excerpt_tr": "2-3 cumlelik ozet",
    "seo_title_tr": "SEO icin optimize baslik (max 60 karakter)",
    "seo_description_tr": "Meta description (max 160 karakter)",
    "suggested_category": "migren|epilepsi|demans|uyku|genel-saglik"
}}

SADECE JSON dondur, baska bir sey yazma."""

    def _parse_response(self, content: str) -> dict:
        """LLM yanitini parse et."""
        import re as regex
        cleaned = content.strip()
        match = regex.search(r'\{.*\}', cleaned, regex.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        logger.warning('ContentAgent: JSON parse hatasi, raw donuyor')
        return {
            'title_tr': '',
            'body_tr': content,
            'excerpt_tr': '',
            'parse_error': True,
        }

    def validate_output(self, output: dict) -> Optional[str]:
        """Cikti dogrulama."""
        if output.get('error'):
            return output['error']
        if not output.get('body_tr') and not output.get('parse_error'):
            return "Icerik body_tr alani bos"
        return None
