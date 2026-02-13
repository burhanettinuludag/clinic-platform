"""
SEO Uzmani Ajan.

Icerik icin SEO optimizasyonu yapar:
- seo_title_tr/en (max 60 karakter)
- seo_description_tr/en (max 160 karakter)
- Schema.org JSON-LD onerisi
- Anahtar kelime onerisi
- E-E-A-T sinyalleri (YMYL uyumu)
- Ic link onerileri

Content Agent'tan sonra, Legal Agent'tan once calisir.
"""

import json
import logging
from typing import Optional

from services.base_agent import BaseAgent
from services.prompts.seo_prompts import SEO_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class SEOAgent(BaseAgent):
    """Saglik icerigi icin SEO optimizasyonu yapan ajan."""

    name = 'seo_agent'
    task_type = 'optimize_seo'
    system_prompt = SEO_SYSTEM_PROMPT
    feature_flag_key = 'agent_seo'
    temperature = 0.3  # SEO icin dusuk yaraticilik, tutarli cikti
    max_tokens = 2000

    def execute(self, input_data: dict) -> dict:
        """
        SEO optimizasyonu yap.

        Input (Content Agent'tan gelir):
            title_tr: str - Makale basligi
            body_tr: str - Makale icerigi
            excerpt_tr: str - Ozet
            seo_title_tr: str - Mevcut SEO basligi (bos olabilir)
            seo_description_tr: str - Mevcut meta description (bos olabilir)
            suggested_category: str - Kategori
            module: str - Hastalik modulu (opsiyonel)

        Output (input_data + SEO alanlari):
            seo_title_tr, seo_title_en,
            seo_description_tr, seo_description_en,
            schema_type, schema_json,
            keywords_tr, keywords_en,
            internal_links, eeat_signals
        """
        title = input_data.get('title_tr', '')
        body = input_data.get('body_tr', '')
        category = input_data.get('suggested_category', 'genel-saglik')
        module = input_data.get('module', 'general')

        if not body:
            return {**input_data, 'seo_error': 'Icerik (body_tr) bos'}

        prompt = self._build_prompt(title, body, category, module)
        response = self.llm_call(prompt)
        seo_data = self._parse_response(response.content)

        # Mevcut input_data ile merge et
        result = {**input_data, **seo_data}
        result['seo_provider'] = response.provider
        result['seo_tokens'] = response.tokens_used
        return result

    def _build_prompt(self, title, body, category, module):
        """SEO optimizasyon prompt'u."""
        module_map = {
            'migraine': 'migren',
            'epilepsy': 'epilepsi',
            'dementia': 'demans / Alzheimer',
            'wellness': 'saglikli yasam',
            'general': 'genel noroloji',
        }
        disease_tr = module_map.get(module, module)

        # Body'yi kisalt (token tasarrufu)
        body_preview = body[:1500] if len(body) > 1500 else body

        return f"""Asagidaki saglik icerigini SEO icin optimize et.

BASLIK: {title}
KATEGORI: {category}
HASTALIK ALANI: {disease_tr}

ICERIK (ilk 1500 karakter):
{body_preview}

GOREVLER:
1. SEO basligi olustur (Turkce + Ingilizce, max 60 karakter)
2. Meta description yaz (Turkce + Ingilizce, max 160 karakter)
3. Schema.org tipi belirle (MedicalCondition, FAQPage, MedicalWebPage, Article)
4. Schema JSON-LD olustur
5. Anahtar kelimeler oner (Turkce 5 adet, Ingilizce 5 adet)
6. E-E-A-T sinyalleri oner (Experience, Expertise, Authoritativeness, Trustworthiness)
7. Ic link onerileri ver (hangi sayfalara link verilmeli)

ONEMLI:
- Bu YMYL (Your Money Your Life) kategorisi icerik - Google ekstra scrutiny uygular
- E-E-A-T zorunlu: Yazar bilgisi (Prof. Dr. Burhanettin Uludag, Noroloji Uzmani, Ege Universitesi)
- Turkce tibbi arama terimleri kullan ("bas agrisi" degil "migren tedavisi" gibi spesifik)

CIKTI FORMATI (JSON):
{{
    "seo_title_tr": "max 60 karakter Turkce SEO basligi",
    "seo_title_en": "max 60 char English SEO title",
    "seo_description_tr": "max 160 karakter Turkce meta description",
    "seo_description_en": "max 160 char English meta description",
    "schema_type": "MedicalCondition|FAQPage|MedicalWebPage|Article",
    "schema_json": {{...schema.org JSON-LD objesi...}},
    "keywords_tr": ["kelime1", "kelime2", "kelime3", "kelime4", "kelime5"],
    "keywords_en": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
    "internal_links": [
        {{"text": "link metni", "path": "/patient/migraine", "reason": "neden link verilmeli"}}
    ],
    "eeat_signals": {{
        "author": "Prof. Dr. Burhanettin Uludag",
        "credentials": "Noroloji Uzmani, Klinik Norofizyoloji Yan Dal Uzmani",
        "institution": "Ege Universitesi Tip Fakultesi",
        "review_note": "Bu icerik noroloji uzmani tarafindan incelenmistir."
    }}
}}

SADECE JSON dondur."""

    def _parse_response(self, content: str) -> dict:
        """LLM yanitini parse et."""
        import re
        cleaned = content.strip()
        match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
                # Uzunluk kontrolu
                if data.get('seo_title_tr') and len(data['seo_title_tr']) > 70:
                    data['seo_title_tr'] = data['seo_title_tr'][:67] + '...'
                if data.get('seo_description_tr') and len(data['seo_description_tr']) > 170:
                    data['seo_description_tr'] = data['seo_description_tr'][:167] + '...'
                return data
            except json.JSONDecodeError:
                pass
        logger.warning('SEOAgent: JSON parse hatasi')
        return {'seo_parse_error': True}

    def validate_output(self, output: dict) -> Optional[str]:
        """Cikti dogrulama."""
        if output.get('seo_error'):
            return output['seo_error']
        if output.get('seo_parse_error'):
            return "SEO ciktisi parse edilemedi"
        if not output.get('seo_title_tr'):
            return "seo_title_tr alani bos"
        return None
