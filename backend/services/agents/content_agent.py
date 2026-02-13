"""
Icerik Uretici Ajan - Ilk ajan implementasyonu.

Blog yazisi, hasta bilgilendirme, egitim icerigi uretir.
Hekim onaylamadan yayinlanmaz (Article.status='draft').
"""

import json
import logging
import re
from typing import Optional

from services.base_agent import BaseAgent
from services.prompts.content_prompts import CONTENT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class ContentAgent(BaseAgent):
    """Blog, bilgilendirme ve egitim icerigi ureten ajan."""

    name = 'content_agent'
    task_type = 'generate_content'
    system_prompt = CONTENT_SYSTEM_PROMPT
    feature_flag_key = 'agent_content'
    temperature = 0.7
    max_tokens = 3000

    def execute(self, input_data: dict) -> dict:
        """
        Icerik uret.

        Input:
            topic: str - Konu
            module: str - Hastalik modulu
            audience: str - Hedef kitle [default: patient]
            tone: str - Ton [default: friendly]
            content_type: str - Icerik tipi [default: blog]

        Output:
            title_tr, body_tr, excerpt_tr,
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
        """LLM yanitini parse et. Backtick, nested newline vb. durumlari handle eder."""
        cleaned = content.strip()

        # 1. Dogrudan JSON parse dene
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # 2. Backtick'leri temizle ve tekrar dene
        cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
        cleaned = re.sub(r'\s*```$', '', cleaned)
        cleaned = cleaned.strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # 3. En dis { } blogu bul
        match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if match:
            raw = match.group(0)
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                pass

            # 4. Key-value extraction (body_tr icinde newline/quote varsa JSON bozulur)
            result = {}
            for key in ['title_tr', 'excerpt_tr', 'seo_title_tr', 'seo_description_tr', 'suggested_category']:
                km = re.search(
                    r'"' + key + r'"\s*:\s*"((?:[^"\\]|\\.)*)"',
                    raw
                )
                if km:
                    result[key] = km.group(1).replace('\\n', '\n').replace('\\"', '"')

            # body_tr ozel: son key'e veya kapanan } a kadar al
            bm = re.search(
                r'"body_tr"\s*:\s*"(.*?)"(?:\s*,\s*"(?:excerpt|seo_|suggested)|\s*\})',
                raw,
                re.DOTALL
            )
            if bm:
                body = bm.group(1).replace('\\n', '\n').replace('\\"', '"')
                result['body_tr'] = body

            if result.get('title_tr') or result.get('body_tr'):
                return result

        # 5. Son care: raw content'i body_tr olarak dondur
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
